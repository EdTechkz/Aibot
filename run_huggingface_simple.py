#!/usr/bin/env python3
"""
🤖 Скрипт запуска AI-бота Шерлока Холмса с Hugging Face API
"""

import os
import sys
import subprocess
import importlib.util
from pathlib import Path

def check_python_version():
    """Проверка версии Python"""
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше")
        print(f"   Текущая версия: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def check_dependencies():
    """Проверка и установка зависимостей"""
    requirements_file = "requirements_huggingface_simple.txt"
    
    if not os.path.exists(requirements_file):
        print(f"❌ Файл {requirements_file} не найден")
        return False
    
    print("📦 Проверка зависимостей...")
    
    # Читаем зависимости
    with open(requirements_file, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    missing_packages = []
    
    for req in requirements:
        package_name = req.split('>=')[0].split('==')[0]
        if importlib.util.find_spec(package_name) is None:
            missing_packages.append(req)
    
    if missing_packages:
        print(f"📥 Установка недостающих пакетов: {len(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", requirements_file
            ])
            print("✅ Зависимости установлены")
        except subprocess.CalledProcessError:
            print("❌ Ошибка установки зависимостей")
            return False
    else:
        print("✅ Все зависимости уже установлены")
    
    return True

def check_api_key():
    """Проверка API ключа"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('HUGGINGFACE_API_KEY', '')
    
    if not api_key:
        print("⚠️  HUGGINGFACE_API_KEY не найден в файле .env")
        print("   Для полной функциональности добавьте API ключ")
        print("   Получить ключ можно на: https://huggingface.co/settings/tokens")
        
        # Создаем пример файла .env
        if not os.path.exists('.env'):
            with open('.env', 'w') as f:
                f.write("# Hugging Face API Key\n")
                f.write("# Получите ключ на: https://huggingface.co/settings/tokens\n")
                f.write("HUGGINGFACE_API_KEY=your_api_key_here\n")
            print("✅ Создан файл .env с примером")
        
        return False
    else:
        print("✅ API ключ найден")
        return True

def check_streamlit():
    """Проверка Streamlit"""
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} - OK")
        return True
    except ImportError:
        print("❌ Streamlit не установлен")
        return False

def check_flask():
    """Проверка Flask"""
    try:
        import flask
        print(f"✅ Flask {flask.__version__} - OK")
        return True
    except ImportError:
        print("❌ Flask не установлен")
        return False

def api_info():
    """Информация о Hugging Face API"""
    print("\n🌐 Информация о Hugging Face API:")
    print("   - Бесплатный API для тестирования")
    print("   - Лимит: 30,000 запросов в месяц")
    print("   - Модель: microsoft/DialoGPT-medium")
    print("   - Скорость: Быстрая (через интернет)")
    print("   - Приватность: Данные отправляются на сервер")

def run_streamlit():
    """Запуск Streamlit приложения"""
    print("\n🚀 Запуск Streamlit приложения...")
    
    try:
        # Запускаем Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app_huggingface_simple.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

def run_flask():
    """Запуск Flask приложения"""
    print("\n🚀 Запуск Flask приложения...")
    
    try:
        # Запускаем Flask
        subprocess.run([
            sys.executable, "app_huggingface_simple.py"
        ])
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

def main():
    """Основная функция"""
    print("🕵️ AI-бот Шерлока Холмса - Hugging Face API версия")
    print("=" * 50)
    
    # Проверки
    if not check_python_version():
        return
    
    if not check_dependencies():
        return
    
    if not check_streamlit():
        return
    
    if not check_flask():
        return
    
    # Проверка API ключа
    api_configured = check_api_key()
    
    # Информация о API
    api_info()
    
    # Выбор интерфейса
    print("\n🎯 Выберите интерфейс:")
    print("1. Streamlit (рекомендуется) - современный веб-интерфейс")
    print("2. Flask - классический веб-интерфейс")
    
    if not api_configured:
        print("\n⚠️  Примечание: Без API ключа функциональность будет ограничена")
    
    while True:
        choice = input("\nВведите номер (1 или 2): ").strip()
        
        if choice == "1":
            run_streamlit()
            break
        elif choice == "2":
            run_flask()
            break
        else:
            print("❌ Неверный выбор. Введите 1 или 2.")

if __name__ == "__main__":
    main() 