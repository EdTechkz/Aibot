#!/usr/bin/env python3
"""
Запуск AI-бота Шерлока Холмса через Streamlit
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")

def check_dependencies():
    """Проверка и установка зависимостей"""
    print("🔍 Проверка зависимостей...")
    
    try:
        import streamlit
        import openai
        import chromadb
        import sentence_transformers
        import requests
        import beautifulsoup4
        print("✅ Все зависимости установлены")
        return True
    except ImportError as e:
        print(f"❌ Отсутствуют зависимости: {e}")
        print("📦 Установка зависимостей...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Зависимости установлены")
            return True
        except subprocess.CalledProcessError:
            print("❌ Ошибка при установке зависимостей")
            return False

def check_env_file():
    """Проверка файла .env"""
    env_file = Path(".env")
    env_example = Path("env_example.txt")
    
    if not env_file.exists():
        if env_example.exists():
            print("⚠️  Файл .env не найден")
            print("📝 Создание .env из примера...")
            
            with open(env_example, 'r') as f:
                content = f.read()
            
            with open(".env", 'w') as f:
                f.write(content)
            
            print("✅ Файл .env создан")
            print("⚠️  Не забудьте добавить ваш OpenAI API ключ в файл .env")
        else:
            print("❌ Файл env_example.txt не найден")
            return False
    
    return True

def check_openai_key():
    """Проверка OpenAI API ключа"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        print("⚠️  OpenAI API ключ не настроен")
        print("🔑 Получите ключ на https://platform.openai.com")
        print("📝 Добавьте ключ в файл .env")
        return False
    
    print("✅ OpenAI API ключ настроен")
    return True

def create_directories():
    """Создание необходимых директорий"""
    directories = ['templates', 'static', 'logs']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Директории созданы")

def main():
    """Основная функция запуска"""
    print("🕵️  Запуск AI-бота Шерлока Холмса (Streamlit)")
    print("=" * 60)
    
    # Проверки
    check_python_version()
    
    if not check_dependencies():
        sys.exit(1)
    
    create_directories()
    
    if not check_env_file():
        sys.exit(1)
    
    if not check_openai_key():
        print("\n⚠️  Приложение запустится, но функции AI будут недоступны")
    
    print("\n🚀 Запуск Streamlit приложения...")
    print("🌐 Приложение будет доступно по адресу: http://localhost:8501")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("=" * 60)
    
    try:
        # Запуск Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено")
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 