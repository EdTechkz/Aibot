import streamlit as st
import openai
import time
import os
from dotenv import load_dotenv
import chromadb
from sentence_transformers import SentenceTransformer
from scraper import WebScraper
from streamlit_chat import message

# Загрузка переменных окружения
load_dotenv()

# Настройка страницы
st.set_page_config(
    page_title="🕵️ Шерлок Холмс - AI Детектив",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Инициализация OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# Инициализация модели для эмбеддингов
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

embedding_model = load_embedding_model()

# Инициализация ChromaDB
@st.cache_resource
def init_chromadb():
    chroma_client = chromadb.Client()
    try:
        collection = chroma_client.get_collection("sherlock_knowledge")
    except:
        collection = chroma_client.create_collection(
            name="sherlock_knowledge",
            metadata={"hnsw:space": "cosine"}
        )
    return chroma_client, collection

chroma_client, collection = init_chromadb()

# Инициализация скрапера
@st.cache_resource
def init_scraper():
    return WebScraper()

scraper = init_scraper()

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
            st.error(f"Ошибка при сохранении в БД: {e}")
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
            st.error(f"Ошибка при поиске контекста: {e}")
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
                with st.spinner("🔍 Шерлок анализирует веб-страницу..."):
                    # Получаем информацию о странице
                    page_info = scraper.get_page_info(url)
                    
                    # Скрапим контент
                    chunks = scraper.scrape_url(url)
                    
                    if chunks and not chunks[0].startswith("Не удалось"):
                        self.store_in_vector_db(chunks, url, page_info)
                        st.success(f"✅ Сайт '{page_info.get('title', url)}' успешно обработан и добавлен в базу знаний")
                    else:
                        st.error(f"❌ Ошибка при обработке URL: {url}")
                        
            except Exception as e:
                st.error(f"Ошибка при скрапинге {url}: {e}")
        
        # Ищем релевантный контекст
        with st.spinner("🔍 Шерлок ищет в своих записях..."):
            context = self.search_relevant_context(user_message)
        
        # Генерируем ответ
        with st.spinner("🕵️ Шерлок размышляет..."):
            response = self.generate_response(user_message, context)
        
        return response

# Инициализация бота
@st.cache_resource
def init_bot():
    return SherlockHolmesBot()

sherlock_bot = init_bot()

# CSS стили
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1a1a1a 0%, #2d2d2d 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h1 {
        color: #ffd700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .main-header p {
        color: #b0b0b0;
        font-style: italic;
        font-size: 1.2rem;
    }
    .feature-card {
        background: rgba(255,255,255,0.1);
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.2);
        margin-bottom: 1rem;
    }
    .stButton > button {
        background: linear-gradient(45deg, #ffd700, #ffed4e);
        color: #1a1a1a;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(255,215,0,0.4);
    }
</style>
""", unsafe_allow_html=True)

# Главный заголовок
st.markdown("""
<div class="main-header">
    <h1>🕵️ Шерлок Холмс</h1>
    <p>"Элементарно, Ватсон!" - AI Детектив с функциями RAG и веб-скрапинга</p>
</div>
""", unsafe_allow_html=True)

# Боковая панель
with st.sidebar:
    st.header("🔧 Инструменты Шерлока")
    
    # Веб-скрапинг
    st.subheader("🌐 Веб-скрапинг")
    url_input = st.text_input("URL для анализа:", placeholder="https://ru.wikipedia.org/wiki/...")
    
    if st.button("🔍 Скрапить сайт", key="scrape_btn"):
        if url_input:
            with st.spinner("🔍 Шерлок анализирует веб-страницу..."):
                try:
                    page_info = scraper.get_page_info(url_input)
                    chunks = scraper.scrape_url(url_input)
                    
                    if chunks and not chunks[0].startswith("Не удалось"):
                        sherlock_bot.store_in_vector_db(chunks, url_input, page_info)
                        st.success(f"✅ Сайт '{page_info.get('title', url_input)}' обработан")
                        st.info(f"📊 Добавлено {len(chunks)} фрагментов в базу знаний")
                    else:
                        st.error("❌ Не удалось обработать сайт")
                except Exception as e:
                    st.error(f"❌ Ошибка: {e}")
        else:
            st.warning("⚠️ Введите URL")
    
    st.divider()
    
    # Статистика
    st.subheader("📊 Статистика")
    try:
        count = collection.count()
        st.metric("Записей в БД", count)
    except:
        st.metric("Записей в БД", 0)
    
    # Очистка базы
    if st.button("🗑️ Очистить базу знаний", key="clear_btn"):
        try:
            chroma_client.delete_collection("sherlock_knowledge")
            collection = chroma_client.create_collection(
                name="sherlock_knowledge",
                metadata={"hnsw:space": "cosine"}
            )
            st.success("✅ База знаний очищена")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Ошибка: {e}")
    
    st.divider()
    
    # Информация
    st.subheader("ℹ️ О боте")
    st.markdown("""
    **Возможности:**
    - 💬 Чат в стиле Шерлока Холмса
    - 🌐 Веб-скрапинг любых сайтов
    - 🔍 RAG система для точных ответов
    - 🕵️ Дедуктивный анализ
    """)

# Основной контент
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Диалог с Шерлоком")
    
    # Инициализация истории чата
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Приветственное сообщение
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Добро пожаловать, дорогой друг! Я Шерлок Холмс, и я готов помочь вам в расследовании. Расскажите мне о деле, которое требует моего внимания, или предоставьте URL для анализа. Элементарно, Ватсон!"
        })

    # Отображение истории чата
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Поле ввода
    if prompt := st.chat_input("Задайте вопрос Шерлоку..."):
        # Добавляем сообщение пользователя
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Генерируем ответ
        with st.chat_message("assistant"):
            with st.spinner("🕵️ Шерлок размышляет..."):
                response = sherlock_bot.process_message(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

with col2:
    st.header("🎯 Быстрые действия")
    
    # Примеры вопросов
    st.subheader("💡 Примеры вопросов")
    
    example_questions = [
        "Расскажи о дедуктивном методе",
        "Какие у тебя хобби?",
        "Где ты живешь?",
        "Как ты относишься к доктору Ватсону?",
        "Что такое криминалистика?"
    ]
    
    for question in example_questions:
        if st.button(question, key=f"example_{question[:20]}"):
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)
            
            with st.chat_message("assistant"):
                with st.spinner("🕵️ Шерлок размышляет..."):
                    response = sherlock_bot.process_message(question)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
    
    st.divider()
    
    # Примеры URL
    st.subheader("🌐 Примеры URL")
    
    example_urls = [
        "https://ru.wikipedia.org/wiki/Шерлок_Холмс",
        "https://ru.wikipedia.org/wiki/Дедукция",
        "https://ru.wikipedia.org/wiki/Криминалистика"
    ]
    
    for url in example_urls:
        if st.button(f"📄 {url.split('/')[-1].replace('_', ' ')}", key=f"url_{url[:20]}"):
            with st.spinner("🔍 Шерлок анализирует веб-страницу..."):
                try:
                    page_info = scraper.get_page_info(url)
                    chunks = scraper.scrape_url(url)
                    
                    if chunks and not chunks[0].startswith("Не удалось"):
                        sherlock_bot.store_in_vector_db(chunks, url, page_info)
                        st.success(f"✅ Сайт обработан")
                        st.info(f"📊 Добавлено {len(chunks)} фрагментов")
                    else:
                        st.error("❌ Не удалось обработать сайт")
                except Exception as e:
                    st.error(f"❌ Ошибка: {e}")

# Футер
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; padding: 1rem;">
    <p>🕵️ AI-бот Шерлока Холмса | Powered by OpenAI GPT & Streamlit</p>
    <p><em>"Когда вы исключили невозможное, то, что остается, и есть правда, как бы невероятно это ни казалось."</em></p>
</div>
""", unsafe_allow_html=True) 