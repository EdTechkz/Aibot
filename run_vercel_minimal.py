#!/usr/bin/env python3
"""
Запуск минимальной версии AI-бота Шерлока Холмса для Vercel
"""

import os
import sys
import subprocess

def install_requirements():
    """Установка минимальных зависимостей"""
    print("📦 Установка минимальных зависимостей...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_vercel_minimal.txt"
        ])
        print("✅ Зависимости установлены!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки зависимостей: {e}")
        return False
    return True

def run_app():
    """Запуск приложения"""
    print("🚀 Запуск минимальной версии...")
    try:
        from vercel_app_minimal import app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Попробуйте установить зависимости: pip install -r requirements_vercel_minimal.txt")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

if __name__ == "__main__":
    print("🤖 Минимальная версия AI-бота Шерлока Холмса")
    print("=" * 50)
    
    # Проверяем зависимости
    try:
        import flask
        import requests
        import bs4
        print("✅ Все зависимости уже установлены")
    except ImportError:
        print("⚠️  Не все зависимости установлены")
        if not install_requirements():
            sys.exit(1)
    
    run_app() 