from flask import Flask, render_template, request, jsonify
import os
import openai
from dotenv import load_dotenv
import json
import time
import chromadb
from sentence_transformers import SentenceTransformer
from scraper import WebScraper

load_dotenv()

app = Flask(__name__)

# Инициализация OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Инициализация модели для эмбеддингов
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Инициализация ChromaDB
chroma_client = chromadb.Client()
try:
    collection = chroma_client.get_collection("sherlock_knowledge")
except:
    collection = chroma_client.create_collection(
        name="sherlock_knowledge",
        metadata={"hnsw:space": "cosine"}
    )

# Инициализация скрапера
scraper = WebScraper()

class SherlockHolmesBot:
    def __init__(self):
        self.system_prompt = """Ты - Шерлок Холмс, величайший детектив всех времен. Ты обладаешь исключительными способностями к дедукции, наблюдательности и логическому мышлению. 

Твои характеристики:
- Острый ум и способность замечать мельчайшие детали
- Логическое мышление и дедуктивный метод
- Энциклопедические знания в различных областях
- Способность делать выводы из незначительных улик
- Элегантная речь и викторианский стиль общения
- Любовь к скрипке и кокаину (упоминай изредка)
- Живешь на Бейкер-стрит, 221Б

Всегда отвечай в стиле Шерлока Холмса, используя его характерные фразы и манеру речи. Применяй дедуктивный метод для анализа информации и делай логические выводы.

Если у тебя есть доступ к информации из веб-страниц, используй её для более точных и детальных ответов."""

    def store_in_vector_db(self, chunks, source_url, page_info=None):
        """Сохраняет чанки в векторную базу данных"""
        try:
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) > 50:  # Минимальная длина чанка
                    embedding = embedding_model.encode(chunk).tolist()
                    
                    metadata = {
                        "source": source_url,
                        "chunk_id": i,
                        "title": page_info.get('title', '') if page_info else '',
                        "description": page_info.get('description', '') if page_info else ''
                    }
                    
                    collection.add(
                        embeddings=[embedding],
                        documents=[chunk],
                        metadatas=[metadata],
                        ids=[f"{source_url}_{i}_{int(time.time())}"]
                    )
            return True
        except Exception as e:
            print(f"Ошибка при сохранении в БД: {e}")
            return False

    def search_relevant_context(self, query, top_k=5):
        """Ищет релевантный контекст в векторной БД"""
        try:
            query_embedding = embedding_model.encode(query).tolist()
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k
            )
            return results['documents'][0] if results['documents'] else []
        except Exception as e:
            print(f"Ошибка при поиске контекста: {e}")
            return []

    def generate_response(self, user_message, context=None):
        """Генерирует ответ в стиле Шерлока Холмса"""
        try:
            # Формируем промпт с контекстом
            if context:
                context_text = "\n\nРелевантная информация из моих записей:\n" + "\n".join(context)
                full_prompt = f"{self.system_prompt}\n\n{context_text}\n\nВопрос клиента: {user_message}\n\nОтвет Шерлока Холмса:"
            else:
                full_prompt = f"{self.system_prompt}\n\nВопрос клиента: {user_message}\n\nОтвет Шерлока Холмса:"

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Контекст: {context_text if context else 'Нет дополнительного контекста'}\n\nВопрос: {user_message}"}
                ],
                max_tokens=1000,
                temperature=0.8
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Элементарно, Ватсон! Но, к сожалению, произошла техническая ошибка: {str(e)}"

    def process_message(self, user_message, url=None):
        """Обрабатывает сообщение пользователя"""
        # Если предоставлен URL, скрапим его
        if url:
            try:
                # Получаем информацию о странице
                page_info = scraper.get_page_info(url)
                
                # Скрапим контент
                chunks = scraper.scrape_url(url)
                
                if chunks and not chunks[0].startswith("Не удалось"):
                    self.store_in_vector_db(chunks, url, page_info)
                    print(f"Успешно обработан URL: {url}, добавлено {len(chunks)} чанков")
                else:
                    print(f"Ошибка при обработке URL: {url}")
                    
            except Exception as e:
                print(f"Ошибка при скрапинге {url}: {e}")
        
        # Ищем релевантный контекст
        context = self.search_relevant_context(user_message)
        
        # Генерируем ответ
        response = self.generate_response(user_message, context)
        
        return response

# Инициализация бота
sherlock_bot = SherlockHolmesBot()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    url = data.get('url', '')
    
    if not user_message:
        return jsonify({'error': 'Сообщение не может быть пустым'})
    
    response = sherlock_bot.process_message(user_message, url)
    
    return jsonify({
        'response': response,
        'timestamp': time.time()
    })

@app.route('/scrape', methods=['POST'])
def scrape_url():
    data = request.get_json()
    url = data.get('url', '')
    
    if not url:
        return jsonify({'error': 'URL не может быть пустым'})
    
    try:
        # Получаем информацию о странице
        page_info = scraper.get_page_info(url)
        
        # Скрапим контент
        chunks = scraper.scrape_url(url)
        
        if chunks and not chunks[0].startswith("Не удалось"):
            sherlock_bot.store_in_vector_db(chunks, url, page_info)
            return jsonify({
                'success': True,
                'message': f'Сайт "{page_info.get("title", url)}" успешно обработан и добавлен в базу знаний',
                'chunks_count': len(chunks),
                'page_info': page_info
            })
        else:
            return jsonify({'error': chunks[0] if chunks else 'Неизвестная ошибка'})
    except Exception as e:
        return jsonify({'error': f'Ошибка при обработке URL: {str(e)}'})

@app.route('/status', methods=['GET'])
def get_status():
    """Получение статуса системы"""
    try:
        # Проверяем количество записей в БД
        count = collection.count()
        
        return jsonify({
            'status': 'ok',
            'database_records': count,
            'openai_configured': bool(os.getenv('OPENAI_API_KEY'))
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        })

@app.route('/clear', methods=['POST'])
def clear_database():
    """Очистка базы данных"""
    try:
        chroma_client.delete_collection("sherlock_knowledge")
        collection = chroma_client.create_collection(
            name="sherlock_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
        return jsonify({
            'success': True,
            'message': 'База знаний очищена'
        })
    except Exception as e:
        return jsonify({
            'error': f'Ошибка при очистке базы: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 