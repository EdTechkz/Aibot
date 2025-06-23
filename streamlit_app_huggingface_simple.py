import streamlit as st
from streamlit_chat import message
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Настройка страницы
st.set_page_config(
    page_title="Шерлок Холмс AI - Hugging Face API",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hugging Face API настройки
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
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

def generate_response(question, context=""):
    """Генерация ответа с использованием Hugging Face API"""
    try:
        if not HUGGINGFACE_API_KEY:
            return "Извините, API ключ Hugging Face не настроен. Пожалуйста, добавьте HUGGINGFACE_API_KEY в файл .env"
        
        # Формируем промпт
        prompt = SHERLOCK_PROMPT.format(context=context, question=question)
        
        # Отправляем запрос к Hugging Face API
        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_length": 200,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False
            }
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
        st.error(f"Ошибка генерации: {e}")
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
        
        return {
            'url': url,
            'title': soup.title.string if soup.title else url,
            'content': text[:2000],  # Ограничиваем размер
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        st.error(f"Ошибка скрапинга: {e}")
        return None

def find_relevant_context(question, scraped_content, top_k=3):
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
        st.error(f"Ошибка поиска контекста: {e}")
        return ""

def main():
    # Заголовок
    st.title("🕵️ Шерлок Холмс AI - Hugging Face API")
    st.markdown("**Детектив-консультант с Hugging Face моделями**")
    
    # Инициализация сессии
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'scraped_content' not in st.session_state:
        st.session_state.scraped_content = []
    
    # Боковая панель
    with st.sidebar:
        st.header("🛠️ Инструменты")
        
        # Статус API
        st.subheader("📊 Статус")
        if HUGGINGFACE_API_KEY:
            st.success("✅ API ключ настроен")
        else:
            st.error("❌ API ключ не настроен")
            st.info("Добавьте HUGGINGFACE_API_KEY в файл .env")
            st.markdown("[Получить ключ](https://huggingface.co/settings/tokens)")
        
        st.info(f"📚 Скраплено сайтов: {len(st.session_state.scraped_content)}")
        
        # Веб-скрапинг
        st.subheader("🌐 Веб-скрапинг")
        url = st.text_input("URL для скрапинга:", placeholder="https://example.com")
        
        if st.button("🔍 Скрапить сайт", type="primary"):
            if url:
                with st.spinner("Скрапинг..."):
                    scraped_data = scrape_website(url)
                    if scraped_data:
                        st.session_state.scraped_content.append(scraped_data)
                        st.success(f"✅ Скраплен: {scraped_data['title']}")
            else:
                st.warning("Введите URL")
        
        # Быстрые действия
        st.subheader("⚡ Быстрые действия")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👋 Поздороваться"):
                st.session_state.messages.append({"role": "user", "content": "Привет! Кто ты такой?"})
        
        with col2:
            if st.button("🕵️ О дедукции"):
                st.session_state.messages.append({"role": "user", "content": "Расскажи о дедуктивном методе"})
        
        # Примеры URL
        st.subheader("📖 Примеры для скрапинга")
        example_urls = [
            "https://ru.wikipedia.org/wiki/Шерлок_Холмс",
            "https://ru.wikipedia.org/wiki/Дедукция",
            "https://ru.wikipedia.org/wiki/Криминалистика"
        ]
        
        for url in example_urls:
            if st.button(f"📄 {url.split('/')[-1].replace('_', ' ')}", key=url):
                with st.spinner("Скрапинг..."):
                    scraped_data = scrape_website(url)
                    if scraped_data:
                        st.session_state.scraped_content.append(scraped_data)
                        st.success(f"✅ Скраплен: {scraped_data['title']}")
    
    # Основной контент
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Чат с Шерлоком")
        
        # Отображение истории чата
        for message_obj in st.session_state.messages:
            if message_obj["role"] == "user":
                message(message_obj["content"], is_user=True, key=f"user_{hash(message_obj['content'])}")
            else:
                message(message_obj["content"], is_user=False, key=f"assistant_{hash(message_obj['content'])}")
        
        # Ввод сообщения
        if prompt := st.chat_input("Задайте вопрос Шерлоку..."):
            # Добавляем сообщение пользователя
            st.session_state.messages.append({"role": "user", "content": prompt})
            message(prompt, is_user=True)
            
            # Поиск релевантного контекста
            context = find_relevant_context(prompt, st.session_state.scraped_content)
            
            # Генерация ответа
            with st.spinner("🕵️ Шерлок размышляет..."):
                response = generate_response(prompt, context)
            
            # Добавляем ответ ассистента
            st.session_state.messages.append({"role": "assistant", "content": response})
            message(response, is_user=False)
    
    with col2:
        st.subheader("📚 База знаний")
        
        if st.session_state.scraped_content:
            for i, content in enumerate(st.session_state.scraped_content):
                with st.expander(f"📄 {content['title'][:30]}..."):
                    st.write(f"**URL:** {content['url']}")
                    st.write(f"**Контент:** {content['content'][:200]}...")
                    
                    if st.button(f"🗑️ Удалить", key=f"delete_{i}"):
                        st.session_state.scraped_content.pop(i)
                        st.rerun()
        else:
            st.info("База знаний пуста. Скрапьте несколько сайтов для начала работы.")
        
        # Очистка базы знаний
        if st.session_state.scraped_content:
            if st.button("🗑️ Очистить базу знаний", type="secondary"):
                st.session_state.scraped_content = []
                st.rerun()
    
    # Футер
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        🤖 Powered by Hugging Face API | 🕵️ Sherlock Holmes AI | 
        <a href='https://github.com/your-repo' target='_blank'>GitHub</a>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 