from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

app = Flask(__name__)

# Упрощенный промпт
SHERLOCK_PROMPT = "Ты - Шерлок Холмс. Отвечай в стиле детектива."

scraped_content = []

def generate_response(question, context=""):
    """Упрощенная генерация ответа"""
    try:
        return generate_fallback_response(question, context)
    except Exception as e:
        return "Извините, произошла ошибка."

def generate_fallback_response(question, context=""):
    """Упрощенные ответы"""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['привет', 'здравствуй', 'hello']):
        return "Добро пожаловать! Я Шерлок Холмс, готов помочь в расследовании."
    
    elif any(word in question_lower for word in ['кто ты', 'представься']):
        return "Шерлок Холмс, детектив-консультант с Бейкер-стрит, 221Б."
    
    elif any(word in question_lower for word in ['помощь', 'что умеешь']):
        return "Дедуктивный анализ, веб-скрапинг, RAG система. Предоставьте URL или задайте вопрос!"
    
    elif any(word in question_lower for word in ['загадка', 'дело', 'проблема']):
        return "Интересно! Расскажите подробности. Детали имеют значение."
    
    elif any(word in question_lower for word in ['ватсон', 'доктор']):
        return "Мой дорогой Ватсон - верный друг и помощник."
    
    elif any(word in question_lower for word in ['лондон', 'бейкер-стрит']):
        return "Бейкер-стрит, 221Б - мой дом и офис в Лондоне."
    
    elif any(word in question_lower for word in ['скрипка', 'музыка']):
        return "Музыка помогает мне думать. Скрипка - мой спутник в размышлениях."
    
    elif context and len(context) > 10:
        return "Контекст извлечен! Готов отвечать на вопросы."
    
    else:
        responses = [
            "Интересное наблюдение. Мой дедуктивный метод в действии!",
            "Хм, это требует анализа. Расскажите больше.",
            "Элементарно! Хотя, возможно, не совсем.",
            "Интересная загадка! Мой ум работает.",
            "Позвольте мне проанализировать это."
        ]
        import random
        return random.choice(responses)

def scrape_website(url):
    """Упрощенный скрапинг"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return {
            'url': url,
            'title': soup.title.string if soup.title else url,
            'content': text[:500],  # Ограничиваем размер
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"Ошибка скрапинга: {e}")
        return None

def find_relevant_context(question, top_k=1):
    """Упрощенный поиск контекста"""
    if not scraped_content:
        return ""
    
    try:
        question_lower = question.lower()
        relevant_chunks = []
        
        for content in scraped_content:
            content_lower = content['content'].lower()
            question_words = set(question_lower.split())
            content_words = set(content_lower.split())
            common_words = question_words.intersection(content_words)
            relevance_score = len(common_words) / len(question_words) if question_words else 0
            
            if relevance_score > 0.1:
                relevant_chunks.append((relevance_score, content['content'][:200]))
        
        relevant_chunks.sort(reverse=True)
        relevant_context = "\n".join([text for _, text in relevant_chunks[:top_k]])
        return relevant_context
        
    except Exception as e:
        print(f"Ошибка поиска контекста: {e}")
        return ""

@app.route('/')
def index():
    return render_template('vercel_minimal.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Сообщение не может быть пустым'})
        
        context = find_relevant_context(message)
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
        
        scraped_data = scrape_website(url)
        
        if scraped_data:
            scraped_content.append(scraped_data)
            
            return jsonify({
                'success': True,
                'message': f'Сайт {url} проанализирован!',
                'title': scraped_data['title'],
                'timestamp': scraped_data['timestamp']
            })
        else:
            return jsonify({'error': 'Не удалось обработать указанный URL'})
        
    except Exception as e:
        print(f"Ошибка скрапинга: {e}")
        return jsonify({'error': 'Произошла ошибка при обработке URL'})

@app.route('/status')
def status():
    return jsonify({
        'status': 'running',
        'model': 'Sherlock Holmes Minimal',
        'scraped_sites': len(scraped_content)
    })

if __name__ == '__main__':
    print("🤖 Запуск AI-бота Шерлока Холмса (минимальная версия)...")
    app.run(host='0.0.0.0', port=5000, debug=True) 