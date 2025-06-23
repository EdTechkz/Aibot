import streamlit as st
from streamlit_chat import message
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
import time

# Настройка страницы
st.set_page_config(
    page_title="Шерлок Холмс AI - Hugging Face",
    page_icon="🕵️",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

@st.cache_resource
def load_models():
    """Загрузка Hugging Face моделей с кэшированием"""
    try:
        with st.spinner("🔄 Загрузка токенизатора..."):
            model_name = "microsoft/DialoGPT-medium"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            tokenizer.pad_token = tokenizer.eos_token
        
        with st.spinner("🔄 Загрузка модели..."):
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None
            )
        
        with st.spinner("🔄 Создание пайплайна..."):
            generator = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_length=512,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        with st.spinner("🔄 Загрузка модели для эмбеддингов..."):
            embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        st.success("✅ Модели успешно загружены!")
        return generator, embedding_model
        
    except Exception as e:
        st.error(f"❌ Ошибка загрузки модели: {e}")
        return None, None

def generate_response(generator, question, context=""):
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
        
        # Разбиваем на части для эмбеддингов
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]
        
        return {
            'url': url,
            'title': soup.title.string if soup.title else url,
            'content': text[:2000],  # Ограничиваем размер
            'chunks': chunks[:10]  # Ограничиваем количество чанков
        }
        
    except Exception as e:
        st.error(f"Ошибка скрапинга: {e}")
        return None

def update_embeddings(embedding_model, scraped_data, scraped_content, content_embeddings):
    """Обновление эмбеддингов для RAG"""
    if not embedding_model:
        return scraped_content, content_embeddings
    
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
        
        st.success(f"✅ Добавлено {len(scraped_data['chunks'])} чанков в базу знаний")
        return scraped_content, content_embeddings
        
    except Exception as e:
        st.error(f"Ошибка обновления эмбеддингов: {e}")
        return scraped_content, content_embeddings

def find_relevant_context(embedding_model, question, content_embeddings, top_k=3):
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
        st.error(f"Ошибка поиска контекста: {e}")
        return ""

def main():
    # Заголовок
    st.title("🕵️ Шерлок Холмс AI - Hugging Face")
    st.markdown("**Детектив-консультант с открытыми AI моделями**")
    
    # Инициализация сессии
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'scraped_content' not in st.session_state:
        st.session_state.scraped_content = []
    
    if 'content_embeddings' not in st.session_state:
        st.session_state.content_embeddings = []
    
    # Загрузка моделей
    generator, embedding_model = load_models()
    
    # Боковая панель
    with st.sidebar:
        st.header("🛠️ Инструменты")
        
        # Статус моделей
        st.subheader("📊 Статус")
        if generator:
            st.success("✅ Модель загружена")
        else:
            st.error("❌ Модель не загружена")
        
        if embedding_model:
            st.success("✅ Эмбеддинги готовы")
        else:
            st.error("❌ Эмбеддинги не готовы")
        
        st.info(f"📚 Скраплено сайтов: {len(st.session_state.scraped_content)}")
        st.info(f"🧠 Чанков в базе: {len(st.session_state.content_embeddings)}")
        
        # Веб-скрапинг
        st.subheader("🌐 Веб-скрапинг")
        url = st.text_input("URL для скрапинга:", placeholder="https://example.com")
        
        if st.button("🔍 Скрапить сайт", type="primary"):
            if url:
                with st.spinner("Скрапинг..."):
                    scraped_data = scrape_website(url)
                    if scraped_data:
                        st.session_state.scraped_content, st.session_state.content_embeddings = update_embeddings(
                            embedding_model, scraped_data, 
                            st.session_state.scraped_content, 
                            st.session_state.content_embeddings
                        )
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
                        st.session_state.scraped_content, st.session_state.content_embeddings = update_embeddings(
                            embedding_model, scraped_data, 
                            st.session_state.scraped_content, 
                            st.session_state.content_embeddings
                        )
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
            context = find_relevant_context(
                embedding_model, prompt, 
                st.session_state.content_embeddings
            )
            
            # Генерация ответа
            with st.spinner("🕵️ Шерлок размышляет..."):
                response = generate_response(generator, prompt, context)
            
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
                        # Удаляем контент и соответствующие эмбеддинги
                        url_to_remove = content['url']
                        st.session_state.scraped_content.pop(i)
                        st.session_state.content_embeddings = [
                            emb for emb in st.session_state.content_embeddings 
                            if emb['source'] != url_to_remove
                        ]
                        st.rerun()
        else:
            st.info("База знаний пуста. Скрапьте несколько сайтов для начала работы.")
        
        # Очистка базы знаний
        if st.session_state.scraped_content:
            if st.button("🗑️ Очистить базу знаний", type="secondary"):
                st.session_state.scraped_content = []
                st.session_state.content_embeddings = []
                st.rerun()
    
    # Футер
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        🤖 Powered by Hugging Face Transformers | 🕵️ Sherlock Holmes AI | 
        <a href='https://github.com/your-repo' target='_blank'>GitHub</a>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 