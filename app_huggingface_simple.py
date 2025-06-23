from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)

# Hugging Face API настройки
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/bigscience/bloomz-560m"
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY', '')

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

# Глобальные переменные для хранения скрапленного контента
scraped_content = []

def generate_response(question, context=""):
    """Генерация ответа с использованием Hugging Face API или предустановленных ответов"""
    try:
        if not HUGGINGFACE_API_KEY or HUGGINGFACE_API_KEY == "your_huggingface_api_key_here":
            # Используем предустановленные ответы, если API ключ не настроен
            return generate_fallback_response(question, context)
        
        # Формируем промпт
        prompt = SHERLOCK_PROMPT.format(context=context, question=question)
        
        # Отправляем запрос к Hugging Face API
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt
        }
        
        response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', '')
                
                # Извлекаем только ответ (после промпта)
                if prompt in generated_text:
                    answer = generated_text[len(prompt):].strip()
                else:
                    answer = generated_text.strip()
                
                # Если ответ слишком длинный, обрезаем
                if len(answer) > 500:
                    answer = answer[:500] + "..."
                
                return answer if answer else "Элементарно, мой дорогой Ватсон! Но мне нужно больше информации для точного ответа."
            else:
                return "Прошу прощения, произошла ошибка в обработке ответа."
        else:
            return f"Ошибка API: {response.status_code} - {response.text}"
        
    except Exception as e:
        print(f"Ошибка генерации: {e}")
        return generate_fallback_response(question, context)

def generate_fallback_response(question, context=""):
    """Генерация ответа без API ключа, используя предустановленные ответы"""
    question_lower = question.lower()
    
    # Простые правила для ответов в стиле Шерлока Холмса
    if any(word in question_lower for word in ['привет', 'здравствуй', 'добрый день']):
        return "Добро пожаловать, дорогой друг! Я Шерлок Холмс, и я готов помочь вам в расследовании. <strong>Элементарно, Ватсон!</strong>"
    
    elif any(word in question_lower for word in ['как дела', 'как ты']):
        return "Превосходно, мой дорогой друг! Мой ум работает как часы, а дедуктивные способности находятся на пике формы. Готов к новым загадкам!"
    
    elif any(word in question_lower for word in ['кто ты', 'расскажи о себе']):
        return "Я Шерлок Холмс, детектив-консультант с Бейкер-стрит, 221Б. Мой дедуктивный метод позволяет мне замечать то, что упускают другие. <em>Когда ты исключишь невозможное, то, что остается, и есть правда, как бы невероятно это ни казалось.</em>"
    
    elif any(word in question_lower for word in ['помощь', 'что умеешь', 'возможности']):
        return "Мои возможности включают: <strong>дедуктивный анализ</strong>, <strong>веб-скрапинг</strong>, <strong>RAG систему</strong> для поиска информации, и, конечно же, <em>викторианский стиль речи</em>. Предоставьте мне URL для анализа или задайте вопрос!"
    
    elif any(word in question_lower for word in ['загадка', 'задача', 'проблема']):
        return "Интересно! Расскажите мне подробности этой загадки. Помните, <strong>детали имеют значение</strong>. Каждый факт может быть ключом к разгадке."
    
    elif any(word in question_lower for word in ['логика', 'дедукция', 'метод']):
        return "Мой дедуктивный метод основан на наблюдении и логике. <em>Вы видите, но не наблюдаете</em>. Я замечаю мельчайшие детали, которые другие упускают, и соединяю их в логическую цепочку."
    
    elif any(word in question_lower for word in ['ватсон', 'доктор']):
        return "Ах, мой дорогой Ватсон! Мой верный друг и помощник. Хотя он иногда не понимает моих методов, его присутствие и записи наших дел бесценны для истории криминалистики."
    
    elif any(word in question_lower for word in ['лондон', 'бейкер-стрит']):
        return "Да, я живу на Бейкер-стрит, 221Б, в Лондоне. Мой дом - это не просто жилище, это центр моих расследований. Здесь я играю на скрипке, провожу химические эксперименты и принимаю клиентов."
    
    elif any(word in question_lower for word in ['скрипка', 'музыка']):
        return "Музыка помогает мне думать, мой дорогой друг. Когда я играю на скрипке, мой ум может сосредоточиться на самых сложных загадках. Это как медитация для дедуктивного мышления."
    
    elif context and len(context) > 10:
        # Если есть контекст из веб-скрапинга
        return f"Интересно! Основываясь на проанализированной информации, я могу сказать следующее: <strong>контекст был успешно извлечен</strong>. Теперь я могу отвечать на вопросы, используя эти данные. Что именно вас интересует?"
    
    else:
        # Общий ответ
        responses = [
            "Хм, интересное наблюдение, мой дорогой друг. Позвольте мне применить свой дедуктивный метод к этому вопросу.",
            "Элементарно! Хотя, возможно, не совсем. Давайте разберем это по порядку.",
            "Интересная загадка! Мой ум уже работает над решением.",
            "Позвольте мне проанализировать эту ситуацию с помощью логики и наблюдения.",
            "Хм, это требует более глубокого анализа. Мой дедуктивный метод в действии!",
            "Интересно! Каждый факт может быть ключом к разгадке. Расскажите больше.",
            "Мой дорогой Ватсон, это классический случай для применения дедуктивного метода!",
            "Позвольте мне применить свой метод: <em>когда ты исключишь невозможное, то, что остается, и есть правда</em>."
        ]
        import random
        return random.choice(responses)

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
        
        return {
            'url': url,
            'title': soup.title.string if soup.title else url,
            'content': text[:2000],  # Ограничиваем размер
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Ошибка скрапинга: {e}")
        return None

def find_relevant_context(question, top_k=3):
    """Поиск релевантного контекста для RAG (упрощенная версия)"""
    if not scraped_content:
        return ""
    
    try:
        # Простой поиск по ключевым словам
        question_lower = question.lower()
        relevant_chunks = []
        
        for content in scraped_content:
            content_lower = content['content'].lower()
            
            # Ищем совпадения слов
            question_words = set(question_lower.split())
            content_words = set(content_lower.split())
            
            # Вычисляем пересечение
            common_words = question_words.intersection(content_words)
            relevance_score = len(common_words) / len(question_words) if question_words else 0
            
            if relevance_score > 0.1:  # Порог релевантности
                relevant_chunks.append((relevance_score, content['content'][:500]))
        
        # Сортируем по релевантности
        relevant_chunks.sort(reverse=True)
        
        # Возвращаем топ контекст
        relevant_context = "\n".join([text for _, text in relevant_chunks[:top_k]])
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
        
        # Добавляем в глобальный список
        scraped_content.append(scraped_data)
        
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
        'api_configured': bool(HUGGINGFACE_API_KEY),
        'scraped_sites': len(scraped_content),
        'model': 'gpt2 (via API)'
    })

if __name__ == '__main__':
    print("🤖 Запуск AI-бота Шерлока Холмса с Hugging Face API...")
    
    if not HUGGINGFACE_API_KEY:
        print("⚠️  Внимание: HUGGINGFACE_API_KEY не настроен!")
        print("   Для полной функциональности добавьте API ключ в файл .env")
        print("   Получить ключ можно на: https://huggingface.co/settings/tokens")
    
    print("🚀 Запуск веб-сервера...")
    app.run(debug=True, host='0.0.0.0', port=5000) 