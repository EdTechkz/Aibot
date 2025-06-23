import streamlit as st
import ollama
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import time

# Загрузка переменных окружения
load_dotenv()

# Настройка страницы
st.set_page_config(
    page_title="🕵️ Шерлок Холмс - AI Детектив (Ollama)",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

class SimpleWebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_url(self, url):
        """Простой скрапинг веб-страницы"""
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
                with st.spinner("🔍 Шерлок анализирует веб-страницу..."):
                    chunks = scraper.scrape_url(url)
                    
                    if chunks and not chunks[0].startswith("Ошибка"):
                        context = chunks[:3]  # Берем первые 3 чанка для контекста
                        st.success(f"✅ Веб-страница успешно проанализирована")
                    else:
                        st.error(f"❌ Ошибка при обработке URL: {url}")
                        
            except Exception as e:
                st.error(f"Ошибка при скрапинге {url}: {e}")
        
        # Генерируем ответ
        with st.spinner("🕵️ Шерлок размышляет..."):
            response = self.generate_response(user_message, context)
        
        return response

# Инициализация компонентов
@st.cache_resource
def init_components():
    return SherlockHolmesBot(), SimpleWebScraper()

sherlock_bot, scraper = init_components()

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
    .ollama-info {
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Главный заголовок
st.markdown("""
<div class="main-header">
    <h1>🕵️ Шерлок Холмс</h1>
    <p>"Элементарно, Ватсон!" - AI Детектив с Ollama</p>
</div>
""", unsafe_allow_html=True)

# Информация об Ollama
st.markdown("""
<div class="ollama-info">
    <h3>🤖 Powered by Ollama</h3>
    <p>Этот бот использует локальные AI модели через Ollama. Убедитесь, что Ollama запущена и модель установлена.</p>
    <p><strong>Установка модели:</strong> <code>ollama pull llama2</code></p>
</div>
""", unsafe_allow_html=True)

# Боковая панель
with st.sidebar:
    st.header("🔧 Инструменты Шерлока")
    
    # Выбор модели Ollama
    st.subheader("🤖 Выбор модели")
    try:
        models = ollama.list()
        model_names = [model['name'] for model in models['models']]
        
        if model_names:
            selected_model = st.selectbox(
                "Выберите модель:",
                model_names,
                index=0 if 'llama2' in model_names else 0
            )
            
            if st.button("🔄 Сменить модель"):
                sherlock_bot = SherlockHolmesBot(selected_model)
                st.success(f"✅ Модель изменена на {selected_model}")
        else:
            st.warning("⚠️ Нет доступных моделей. Установите модель: ollama pull llama2")
    except Exception as e:
        st.error(f"❌ Ошибка подключения к Ollama: {e}")
        st.info("💡 Убедитесь, что Ollama запущена: ollama serve")
    
    st.divider()
    
    # Веб-скрапинг
    st.subheader("🌐 Веб-скрапинг")
    url_input = st.text_input("URL для анализа:", placeholder="https://ru.wikipedia.org/wiki/...")
    
    if st.button("🔍 Скрапить сайт", key="scrape_btn"):
        if url_input:
            with st.spinner("🔍 Шерлок анализирует веб-страницу..."):
                try:
                    page_info = scraper.get_page_info(url_input)
                    chunks = scraper.scrape_url(url_input)
                    
                    if chunks and not chunks[0].startswith("Ошибка"):
                        st.success(f"✅ Сайт '{page_info.get('title', url_input)}' обработан")
                        st.info(f"📊 Получено {len(chunks)} фрагментов")
                        
                        # Сохраняем в session state для использования в чате
                        st.session_state.current_url = url_input
                        st.session_state.current_chunks = chunks
                    else:
                        st.error("❌ Не удалось обработать сайт")
                except Exception as e:
                    st.error(f"❌ Ошибка: {e}")
        else:
            st.warning("⚠️ Введите URL")
    
    st.divider()
    
    # Информация
    st.subheader("ℹ️ О боте")
    st.markdown("""
    **Возможности:**
    - 💬 Чат в стиле Шерлока Холмса
    - 🌐 Веб-скрапинг любых сайтов
    - 🕵️ Дедуктивный анализ
    - 🎨 Современный интерфейс
    - 🤖 Локальные AI модели
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
                # Используем текущий URL и чанки из session state
                current_url = st.session_state.get('current_url')
                current_chunks = st.session_state.get('current_chunks')
                
                response = sherlock_bot.process_message(prompt, current_url, scraper)
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
                    
                    if chunks and not chunks[0].startswith("Ошибка"):
                        st.session_state.current_url = url
                        st.session_state.current_chunks = chunks
                        st.success(f"✅ Сайт обработан")
                        st.info(f"📊 Получено {len(chunks)} фрагментов")
                    else:
                        st.error("❌ Не удалось обработать сайт")
                except Exception as e:
                    st.error(f"❌ Ошибка: {e}")

# Футер
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; padding: 1rem;">
    <p>🕵️ AI-бот Шерлока Холмса | Powered by Ollama & Streamlit</p>
    <p><em>"Когда вы исключили невозможное, то, что остается, и есть правда, как бы невероятно это ни казалось."</em></p>
</div>
""", unsafe_allow_html=True) 