#!/usr/bin/env python3
"""
🤖 Скрипт запуска AI-бота Шерлока Холмса с Hugging Face моделями
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
    requirements_file = "requirements_huggingface.txt"
    
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

def check_torch():
    """Проверка PyTorch и CUDA"""
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__} - OK")
        
        if torch.cuda.is_available():
            print(f"🚀 CUDA доступна: {torch.cuda.get_device_name(0)}")
            print(f"   Память GPU: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
        else:
            print("💻 Использование CPU")
        
        return True
    except ImportError:
        print("❌ PyTorch не установлен")
        return False

def check_transformers():
    """Проверка Transformers"""
    try:
        import transformers
        print(f"✅ Transformers {transformers.__version__} - OK")
        return True
    except ImportError:
        print("❌ Transformers не установлен")
        return False

def check_streamlit():
    """Проверка Streamlit"""
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} - OK")
        return True
    except ImportError:
        print("❌ Streamlit не установлен")
        return False

def download_model_info():
    """Информация о загрузке модели"""
    print("\n📥 Информация о загрузке модели:")
    print("   - Первый запуск займет 5-10 минут")
    print("   - Модель будет скачана автоматически")
    print("   - Размер модели: ~1.5 GB")
    print("   - Требуется стабильное интернет-соединение")
    print("   - Модель сохранится локально для повторного использования")

def run_streamlit():
    """Запуск Streamlit приложения"""
    print("\n🚀 Запуск Streamlit приложения...")
    
    try:
        # Запускаем Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "streamlit_app_huggingface.py",
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
            sys.executable, "app_huggingface.py"
        ])
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

def main():
    """Основная функция"""
    print("🕵️ AI-бот Шерлока Холмса - Hugging Face версия")
    print("=" * 50)
    
    # Проверки
    if not check_python_version():
        return
    
    if not check_dependencies():
        return
    
    if not check_torch():
        return
    
    if not check_transformers():
        return
    
    if not check_streamlit():
        return
    
    # Информация о модели
    download_model_info()
    
    # Выбор интерфейса
    print("\n🎯 Выберите интерфейс:")
    print("1. Streamlit (рекомендуется) - современный веб-интерфейс")
    print("2. Flask - классический веб-интерфейс")
    
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