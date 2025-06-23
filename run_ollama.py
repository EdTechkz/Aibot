#!/usr/bin/env python3
"""
🕵️ Запуск AI-бота Шерлока Холмса с Ollama

Этот скрипт запускает Streamlit приложение с локальными AI моделями через Ollama.
"""

import subprocess
import sys
import os

def check_ollama():
    """Проверяет, установлена ли Ollama"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama установлена: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama не найдена")
            return False
    except FileNotFoundError:
        print("❌ Ollama не установлена")
        return False

def check_ollama_service():
    """Проверяет, запущен ли сервис Ollama"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Сервис Ollama запущен")
            return True
        else:
            print("❌ Сервис Ollama не запущен")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к Ollama: {e}")
        return False

def install_model(model_name="llama2"):
    """Устанавливает модель Ollama"""
    print(f"📥 Установка модели {model_name}...")
    try:
        result = subprocess.run(['ollama', 'pull', model_name], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Модель {model_name} установлена")
            return True
        else:
            print(f"❌ Ошибка установки модели {model_name}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def run_streamlit():
    """Запускает Streamlit приложение"""
    print("🚀 Запуск Streamlit приложения...")
    try:
        subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'streamlit_app_ollama.py'])
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

def main():
    """Основная функция"""
    print("🕵️ AI-бот Шерлока Холмса с Ollama")
    print("=" * 50)
    
    # Проверяем Ollama
    if not check_ollama():
        print("\n📋 Для установки Ollama:")
        print("1. Перейдите на https://ollama.ai")
        print("2. Скачайте и установите Ollama")
        print("3. Запустите: ollama serve")
        return
    
    # Проверяем сервис
    if not check_ollama_service():
        print("\n🔧 Запустите сервис Ollama:")
        print("ollama serve")
        return
    
    # Проверяем модели
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if 'llama2' not in result.stdout:
            print("\n📥 Модель llama2 не найдена")
            install = input("Установить модель llama2? (y/n): ")
            if install.lower() == 'y':
                if not install_model("llama2"):
                    return
            else:
                print("⚠️ Убедитесь, что у вас установлена хотя бы одна модель")
        else:
            print("✅ Модель llama2 найдена")
    except Exception as e:
        print(f"❌ Ошибка проверки моделей: {e}")
        return
    
    print("\n🎯 Готово к запуску!")
    print("📝 Приложение будет доступно по адресу: http://localhost:8501")
    print("🛑 Для остановки нажмите Ctrl+C")
    print("=" * 50)
    
    # Запускаем приложение
    run_streamlit()

if __name__ == "__main__":
    main() 