#!/usr/bin/env python3
"""
Скрипт для запуска AI-бота Шерлока Холмса с HuggingChat интеграцией
"""

import os
import sys
import subprocess
import signal
import time

def check_dependencies():
    """Проверка необходимых зависимостей"""
    required_packages = [
        'flask',
        'requests', 
        'beautifulsoup4',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Отсутствуют необходимые пакеты:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Установка зависимостей...")
        
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ Зависимости установлены!")
        except subprocess.CalledProcessError:
            print("❌ Ошибка установки зависимостей")
            return False
    
    return True

def stop_existing_processes():
    """Остановка процессов на порту 5000"""
    try:
        # Поиск процессов на порту 5000
        result = subprocess.run(['lsof', '-ti:5000'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"🛑 Остановка процессов на порту 5000: {pids}")
            
            for pid in pids:
                if pid:
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        time.sleep(1)
                        os.kill(int(pid), signal.SIGKILL)
                    except ProcessLookupError:
                        pass
            
            time.sleep(2)
            print("✅ Процессы остановлены")
    except FileNotFoundError:
        print("⚠️  lsof не найден, пропускаем проверку портов")
    except Exception as e:
        print(f"⚠️  Ошибка при остановке процессов: {e}")

def main():
    """Основная функция запуска"""
    print("🤖 Запуск AI-бота Шерлока Холмса с HuggingChat интеграцией...")
    print("=" * 60)
    
    # Проверка зависимостей
    if not check_dependencies():
        print("❌ Не удалось установить зависимости")
        return
    
    # Остановка существующих процессов
    stop_existing_processes()
    
    # Проверка наличия файла приложения
    app_file = 'app_huggingchat.py'
    if not os.path.exists(app_file):
        print(f"❌ Файл {app_file} не найден")
        return
    
    print("🚀 Запуск веб-сервера...")
    print("🌐 Откройте браузер: http://localhost:5000")
    print("📖 HuggingChat: https://huggingface.co/chat")
    print("=" * 60)
    print("💡 Для остановки нажмите Ctrl+C")
    print("=" * 60)
    
    try:
        # Запуск Flask приложения
        subprocess.run([sys.executable, app_file])
    except KeyboardInterrupt:
        print("\n🛑 Сервер остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")

if __name__ == '__main__':
    main() 