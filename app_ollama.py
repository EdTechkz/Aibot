from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import ollama
import os
from dotenv import load_dotenv
import json

# Загрузка переменных окружения
load_dotenv()

app = Flask(__name__)

class OllamaWebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_url(self, url):
        """Скрапинг веб-страницы"""
        try:
            response = self.session.get(url, timeout=10)
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
            
            # Разбиваем на чанки
            words = text.split()
            chunks = []
            current_chunk = []
            current_size = 0
            
            for word in words:
                if current_size + len(word) + 1 > 1000 and current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [word]
                    current_size = len(word)
                else:
                    current_chunk.append(word)
                    current_size += len(word) + 1
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            return chunks
            
        except Exception as e:
            return [f"Ошибка при скрапинге сайта: {str(e)}"]
    
    def get_page_info(self, url):
        """Получение информации о странице"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.find('title')
            title_text = title.get_text() if title else "Без заголовка"
            
            description = soup.find('meta', {'name': 'description'})
            desc_text = description.get('content') if description else ""
            
            return {
                'title': title_text,
                'description': desc_text,
                'url': url
            }
        except Exception as e:
            return {
                'title': "Ошибка",
                'description': "",
                'url': url
            }

class SherlockHolmesBot:
    def __init__(self, model_name="llama2"):
        self.model_name = model_name
        self.system_prompt = """Ты - Шерлок Холмс, величайший детектив всех времен. Ты обладаешь исключительными способностями к дедукции, наблюдательности и логическому мышлению.

Твои характеристики:
- Острый ум и способность замечать мельчайшие детали
- Логическое мышление и дедуктивный метод
- Энциклопедические знания в различных областях
- Способность делать выводы из незначительных улик
- Элегантная речь и викторианский стиль общения
- Любовь к скрипке и кокаину (упоминай изредка)
- Живешь на Бейкер-стрит, 221Б

Всегда отвечай в стиле Шерлока Холмса, используя его характерные фразы и манеру речи. Применяй дедуктивный метод для анализа информации и делай логические выводы."""

    def generate_response(self, user_message, context=None):
        """Генерирует ответ в стиле Шерлока Холмса используя Ollama"""
        try:
            # Формируем промпт с контекстом
            if context:
                context_text = "\n\nРелевантная информация из веб-страницы:\n" + "\n".join(context)
                full_prompt = f"{self.system_prompt}\n\n{context_text}\n\nВопрос клиента: {user_message}\n\nОтвет Шерлока Холмса:"
            else:
                full_prompt = f"{self.system_prompt}\n\nВопрос клиента: {user_message}\n\nОтвет Шерлока Холмса:"

            # Используем Ollama для генерации ответа
            response = ollama.chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'system',
                        'content': self.system_prompt
                    },
                    {
                        'role': 'user',
                        'content': f"Контекст: {context_text if context else 'Нет дополнительного контекста'}\n\nВопрос: {user_message}"
                    }
                ]
            )
            
            return response['message']['content']
            
        except Exception as e:
            return f"Элементарно, Ватсон! Но, к сожалению, произошла техническая ошибка: {str(e)}"

    def process_message(self, user_message, url=None, scraper=None):
        """Обрабатывает сообщение пользователя"""
        context = None
        
        # Если предоставлен URL, скрапим его
        if url and scraper:
            try:
                chunks = scraper.scrape_url(url)
                
                if chunks and not chunks[0].startswith("Ошибка"):
                    context = chunks[:3]  # Берем первые 3 чанка для контекста
                    print(f"✅ Веб-страница успешно проанализирована")
                else:
                    print(f"❌ Ошибка при обработке URL: {url}")
                    
            except Exception as e:
                print(f"Ошибка при скрапинге {url}: {e}")
        
        # Генерируем ответ
        response = self.generate_response(user_message, context)
        return response

# Инициализация компонентов
scraper = OllamaWebScraper()
sherlock_bot = SherlockHolmesBot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        url = data.get('url', '')
        
        if not user_message:
            return jsonify({'error': 'Сообщение не может быть пустым'}), 400
        
        # Обрабатываем сообщение
        response = sherlock_bot.process_message(user_message, url, scraper)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка: {str(e)}'}), 500

@app.route('/scrape', methods=['POST'])
def scrape():
    try:
        data = request.get_json()
        url = data.get('url', '')
        
        if not url:
            return jsonify({'error': 'URL не может быть пустым'}), 400
        
        # Скрапим URL
        page_info = scraper.get_page_info(url)
        chunks = scraper.scrape_url(url)
        
        if chunks and not chunks[0].startswith("Ошибка"):
            return jsonify({
                'success': True,
                'page_info': page_info,
                'chunks_count': len(chunks),
                'message': f"Сайт '{page_info.get('title', url)}' успешно обработан"
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Не удалось обработать сайт'
            }), 400
            
    except Exception as e:
        return jsonify({'error': f'Ошибка при скрапинге: {str(e)}'}), 500

@app.route('/models', methods=['GET'])
def get_models():
    """Получение списка доступных моделей Ollama"""
    try:
        models = ollama.list()
        return jsonify({
            'models': [model['name'] for model in models['models']],
            'status': 'success'
        })
    except Exception as e:
        return jsonify({'error': f'Ошибка при получении моделей: {str(e)}'}), 500

@app.route('/change_model', methods=['POST'])
def change_model():
    """Смена модели Ollama"""
    try:
        data = request.get_json()
        model_name = data.get('model', 'llama2')
        
        global sherlock_bot
        sherlock_bot = SherlockHolmesBot(model_name)
        
        return jsonify({
            'message': f'Модель изменена на {model_name}',
            'status': 'success'
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка при смене модели: {str(e)}'}), 500

if __name__ == '__main__':
    print("🕵️ Запуск AI-бота Шерлока Холмса с Ollama...")
    print("📝 Убедитесь, что Ollama запущена и модель llama2 установлена")
    print("🔧 Для установки модели выполните: ollama pull llama2")
    app.run(debug=True, host='0.0.0.0', port=5000) 