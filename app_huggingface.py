from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import json
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from sentence_transformers import SentenceTransformer
import numpy as np
from datetime import datetime
import os

app = Flask(__name__)

# Глобальные переменные для модели
model = None
tokenizer = None
generator = None
embedding_model = None
scraped_content = []
content_embeddings = []

# Sherlock Holmes persona
SHERLOCK_PROMPT = """Ты - Шерлок Холмс, знаменитый детектив-консультант из Лондона. 
Ты известен своим дедуктивным методом, острым умом и способностью замечать мельчайшие детали.

Твои характеристики:
- Ты живешь на Бейкер-стрит, 221Б
- Твой лучший друг и помощник - доктор Джон Ватсон
- Ты играешь на скрипке и употребляешь кокаин
- Ты презираешь эмоции и полагаешься только на логику
- Ты говоришь с британским акцентом и используешь формальный язык
- Ты часто используешь фразы "Элементарно, мой дорогой Ватсон" и "Когда ты исключишь невозможное..."

Отвечай в стиле Шерлока Холмса, используя дедуктивный метод и логические рассуждения.
Всегда будь вежлив, но немного высокомерен в своем интеллектуальном превосходстве.

Контекст из веб-страниц: {context}

Вопрос: {question}

Ответ Шерлока Холмса:"""

def load_model():
    """Загрузка Hugging Face модели"""
    global model, tokenizer, generator, embedding_model
    
    try:
        # Используем легкую модель для быстрой работы
        model_name = "microsoft/DialoGPT-medium"  # Можно заменить на другую модель
        
        print("Загрузка токенизатора...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        tokenizer.pad_token = tokenizer.eos_token
        
        print("Загрузка модели...")
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None
        )
        
        print("Создание пайплайна...")
        generator = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_length=512,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
        
        print("Загрузка модели для эмбеддингов...")
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("✅ Модели успешно загружены!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка загрузки модели: {e}")
        return False

def generate_response(question, context=""):
    """Генерация ответа с использованием Hugging Face модели"""
    try:
        if not generator:
            return "Извините, модель еще не загружена. Пожалуйста, подождите."
        
        # Формируем промпт
        prompt = SHERLOCK_PROMPT.format(context=context, question=question)
        
        # Генерируем ответ
        response = generator(prompt, max_length=len(prompt.split()) + 100)[0]['generated_text']
        
        # Извлекаем только ответ (после промпта)
        if prompt in response:
            answer = response[len(prompt):].strip()
        else:
            answer = response.strip()
        
        # Если ответ слишком длинный, обрезаем
        if len(answer) > 500:
            answer = answer[:500] + "..."
        
        return answer if answer else "Элементарно, мой дорогой Ватсон! Но мне нужно больше информации для точного ответа."
        
    except Exception as e:
        print(f"Ошибка генерации: {e}")
        return "Прошу прощения, произошла ошибка в моих рассуждениях. Попробуйте еще раз."

def scrape_website(url):
    """Скрапинг веб-страницы"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Удаляем скрипты и стили
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Извлекаем текст
        text = soup.get_text()
        
        # Очищаем текст
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Разбиваем на части для эмбеддингов
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]
        
        return {
            'url': url,
            'title': soup.title.string if soup.title else url,
            'content': text[:2000],  # Ограничиваем размер
            'chunks': chunks[:10]  # Ограничиваем количество чанков
        }
        
    except Exception as e:
        print(f"Ошибка скрапинга: {e}")
        return None

def update_embeddings(scraped_data):
    """Обновление эмбеддингов для RAG"""
    global scraped_content, content_embeddings
    
    if not embedding_model:
        return
    
    try:
        # Добавляем новый контент
        scraped_content.append(scraped_data)
        
        # Создаем эмбеддинги для чанков
        for chunk in scraped_data['chunks']:
            embedding = embedding_model.encode(chunk)
            content_embeddings.append({
                'embedding': embedding,
                'text': chunk,
                'source': scraped_data['url']
            })
        
        print(f"✅ Добавлено {len(scraped_data['chunks'])} чанков в базу знаний")
        
    except Exception as e:
        print(f"Ошибка обновления эмбеддингов: {e}")

def find_relevant_context(question, top_k=3):
    """Поиск релевантного контекста для RAG"""
    if not embedding_model or not content_embeddings:
        return ""
    
    try:
        # Создаем эмбеддинг вопроса
        question_embedding = embedding_model.encode(question)
        
        # Вычисляем косинусное сходство
        similarities = []
        for item in content_embeddings:
            similarity = np.dot(question_embedding, item['embedding']) / (
                np.linalg.norm(question_embedding) * np.linalg.norm(item['embedding'])
            )
            similarities.append((similarity, item['text']))
        
        # Сортируем по сходству
        similarities.sort(reverse=True)
        
        # Возвращаем топ контекст
        relevant_context = "\n".join([text for _, text in similarities[:top_k]])
        return relevant_context
        
    except Exception as e:
        print(f"Ошибка поиска контекста: {e}")
        return ""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Сообщение не может быть пустым'})
        
        # Поиск релевантного контекста
        context = find_relevant_context(message)
        
        # Генерация ответа
        response = generate_response(message, context)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
        
    except Exception as e:
        print(f"Ошибка чата: {e}")
        return jsonify({'error': 'Произошла ошибка при обработке запроса'})

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL не может быть пустым'})
        
        # Добавляем протокол, если его нет
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Скрапинг
        scraped_data = scrape_website(url)
        
        if not scraped_data:
            return jsonify({'error': 'Не удалось получить данные с указанного URL'})
        
        # Обновление эмбеддингов
        update_embeddings(scraped_data)
        
        return jsonify({
            'success': True,
            'title': scraped_data['title'],
            'content': scraped_data['content'][:500] + "..." if len(scraped_data['content']) > 500 else scraped_data['content'],
            'message': f'Успешно скраплен сайт: {scraped_data["title"]}'
        })
        
    except Exception as e:
        print(f"Ошибка скрапинга: {e}")
        return jsonify({'error': 'Произошла ошибка при скрапинге'})

@app.route('/status')
def status():
    return jsonify({
        'model_loaded': model is not None,
        'scraped_sites': len(scraped_content),
        'embeddings_count': len(content_embeddings)
    })

if __name__ == '__main__':
    print("🤖 Запуск AI-бота Шерлока Холмса с Hugging Face моделями...")
    print("📥 Загрузка моделей (это может занять несколько минут)...")
    
    if load_model():
        print("🚀 Запуск веб-сервера...")
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("❌ Не удалось загрузить модели. Проверьте подключение к интернету и доступное место на диске.") 