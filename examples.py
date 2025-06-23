"""
Примеры использования AI-бота Шерлока Холмса
"""

from app import sherlock_bot
from scraper import WebScraper
import time

def example_basic_chat():
    """Пример базового чата"""
    print("=== Пример базового чата ===")
    
    questions = [
        "Расскажи о дедуктивном методе",
        "Как ты относишься к доктору Ватсону?",
        "Какие у тебя хобби?",
        "Где ты живешь?"
    ]
    
    for question in questions:
        print(f"\n👤 Пользователь: {question}")
        response = sherlock_bot.process_message(question)
        print(f"🕵️  Шерлок: {response}")
        time.sleep(1)

def example_wikipedia_scraping():
    """Пример скрапинга Wikipedia"""
    print("\n=== Пример скрапинга Wikipedia ===")
    
    urls = [
        "https://ru.wikipedia.org/wiki/Шерлок_Холмс",
        "https://ru.wikipedia.org/wiki/Дедукция",
        "https://ru.wikipedia.org/wiki/Конан_Дойл"
    ]
    
    scraper = WebScraper()
    
    for url in urls:
        print(f"\n🌐 Скрапинг: {url}")
        try:
            chunks = scraper.scrape_url(url)
            print(f"✅ Получено {len(chunks)} чанков")
            
            # Добавляем в базу знаний
            sherlock_bot.store_in_vector_db(chunks, url)
            print("✅ Добавлено в базу знаний")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        time.sleep(2)

def example_rag_analysis():
    """Пример RAG анализа"""
    print("\n=== Пример RAG анализа ===")
    
    questions = [
        "Что ты знаешь о Шерлоке Холмсе?",
        "Расскажи о дедуктивном методе",
        "Кто такой Конан Дойл?",
        "Какие методы расследования ты используешь?"
    ]
    
    for question in questions:
        print(f"\n👤 Пользователь: {question}")
        response = sherlock_bot.process_message(question)
        print(f"🕵️  Шерлок: {response}")
        time.sleep(1)

def example_case_solving():
    """Пример решения дела"""
    print("\n=== Пример решения дела ===")
    
    case = """
    Дело: Пропажа драгоценного кольца
    
    Факты:
    - Кольцо пропало из спальни миссис Хадсон
    - Дверь была заперта изнутри
    - Окно было открыто
    - На подоконнике найдены следы грязи
    - В доме был только миссис Хадсон и её кот
    - Кольцо было надето на палец утром
    - Вечером кольцо исчезло
    """
    
    print(f"📋 {case}")
    
    questions = [
        "Проанализируй это дело",
        "Кто мог украсть кольцо?",
        "Как преступник проник в комнату?",
        "Какие улики ты видишь?",
        "Какой твой вердикт?"
    ]
    
    for question in questions:
        print(f"\n👤 Пользователь: {question}")
        response = sherlock_bot.process_message(question)
        print(f"🕵️  Шерлок: {response}")
        time.sleep(1)

def example_website_analysis():
    """Пример анализа веб-сайта"""
    print("\n=== Пример анализа веб-сайта ===")
    
    # Скрапим сайт о криминалистике
    url = "https://ru.wikipedia.org/wiki/Криминалистика"
    
    print(f"🌐 Анализируем сайт: {url}")
    
    try:
        # Скрапим сайт
        scraper = WebScraper()
        chunks = scraper.scrape_url(url)
        
        if chunks and not chunks[0].startswith("Не удалось"):
            sherlock_bot.store_in_vector_db(chunks, url)
            print(f"✅ Сайт обработан, добавлено {len(chunks)} фрагментов")
            
            # Задаем вопросы на основе скрапленного контента
            questions = [
                "Что такое криминалистика?",
                "Какие методы используются в криминалистике?",
                "Как криминалистика связана с дедуктивным методом?",
                "Какие инструменты используют криминалисты?"
            ]
            
            for question in questions:
                print(f"\n👤 Пользователь: {question}")
                response = sherlock_bot.process_message(question)
                print(f"🕵️  Шерлок: {response}")
                time.sleep(1)
        else:
            print("❌ Не удалось обработать сайт")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def run_all_examples():
    """Запуск всех примеров"""
    print("🕵️  Демонстрация возможностей AI-бота Шерлока Холмса")
    print("=" * 60)
    
    try:
        example_basic_chat()
        example_wikipedia_scraping()
        example_rag_analysis()
        example_case_solving()
        example_website_analysis()
        
        print("\n" + "=" * 60)
        print("✅ Все примеры выполнены успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при выполнении примеров: {e}")

if __name__ == "__main__":
    run_all_examples() 