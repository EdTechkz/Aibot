# 🕵️ AI-бот Шерлока Холмсаgit 

Интеллектуальный AI-бот в образе Шерлока Холмса с функциями веб-скрапинга и дедуктивного анализа. Поддерживает множественные AI модели и платформы развертывания.

## 🚀 Быстрый старт

### Вариант 1: Ollama (Рекомендуется - Бесплатно)

```bash
# 1. Установите Ollama
# Перейдите на https://ollama.ai и скачайте для вашей ОС

# 2. Запустите сервис
ollama serve

# 3. Установите модель
ollama pull llama2

# 4. Запустите приложение
python run_ollama.py
```

### Вариант 2: OpenAI (Требует API ключ)

```bash
# 1. Установите зависимости
pip install -r requirements.txt

# 2. Создайте .env файл
echo "OPENAI_API_KEY=your_api_key_here" > .env

# 3. Запустите приложение
python run_streamlit.py
```

### Вариант 3: Flask веб-версия

```bash
# 1. Установите зависимости
pip install -r requirements.txt

# 2. Запустите Flask
python app.py

# 3. Откройте http://localhost:5000
```

## 🎯 Возможности

### 🤖 AI Модели
- **Ollama** - локальные модели (бесплатно)
- **OpenAI GPT** - облачные модели (платно)
- **Hugging Face** - открытые модели
- **Google Gemini** - альтернатива OpenAI

### 🌐 Веб-скрапинг
- Анализ любых веб-страниц
- Извлечение контекста для AI
- Поддержка Wikipedia и других сайтов
- Автоматическая обработка контента

### 🕵️ Дедуктивный анализ
- Логические выводы в стиле Шерлока
- Анализ улик и фактов
- Викторианский стиль общения
- Персонализированные ответы

### 🎨 Интерфейсы
- **Streamlit** - современный веб-интерфейс
- **Flask** - классический веб-сервер
- **Vercel** - облачное развертывание
- **Локальный** - полная приватность

## 📁 Структура проекта

```
Aibot/
├── 🤖 Ollama версия
│   ├── app_ollama.py              # Flask с Ollama
│   ├── streamlit_app_ollama.py    # Streamlit с Ollama
│   ├── run_ollama.py              # Автозапуск
│   ├── requirements_ollama.txt    # Зависимости
│   └── OLLAMA_GUIDE.md           # Руководство
│
├── ☁️ OpenAI версия
│   ├── app.py                     # Flask с OpenAI
│   ├── streamlit_app.py           # Streamlit с OpenAI
│   ├── run_streamlit.py           # Запуск Streamlit
│   └── requirements.txt           # Зависимости
│
├── 🚀 Vercel версия
│   ├── vercel_app.py              # Адаптированная версия
│   ├── requirements_vercel.txt    # Упрощенные зависимости
│   ├── vercel.json                # Конфигурация
│   ├── VERCEL_DEPLOYMENT.md       # Инструкции
│   └── VERCEL_SETUP.md           # Настройка
│
├── 📚 Документация
│   ├── README.md                  # Основное руководство
│   ├── QUICKSTART.md              # Быстрый старт
│   ├── DEPLOYMENT.md              # Развертывание
│   └── STREAMLIT_GUIDE.md        # Streamlit руководство
│
└── 🛠️ Утилиты
    ├── scraper.py                 # Веб-скрапинг
    ├── utils.py                   # Вспомогательные функции
    ├── examples.py                # Примеры использования
    └── templates/                 # HTML шаблоны
```

## 🎮 Использование

### Основные команды

```bash
# Чат с Шерлоком
"Расскажи о дедуктивном методе"
"Какие у тебя хобби?"
"Как ты относишься к доктору Ватсону?"

# Веб-скрапинг
https://ru.wikipedia.org/wiki/Шерлок_Холмс
https://ru.wikipedia.org/wiki/Дедукция
https://ru.wikipedia.org/wiki/Криминалистика
```

### Примеры взаимодействия

1. **Прямой вопрос**: "Кто ты такой?"
2. **Анализ контента**: Скрапьте сайт и задайте вопросы о нем
3. **Дедуктивные выводы**: "Что ты можешь сказать об этом деле?"
4. **Смена модели**: Выберите другую AI модель в интерфейсе

## 🔧 Настройка

### Ollama (Рекомендуется)

```bash
# Установка Ollama
# macOS: скачайте .dmg с ollama.ai
# Windows: скачайте .exe с ollama.ai
# Linux: curl -fsSL https://ollama.ai/install.sh | sh

# Запуск сервиса
ollama serve

# Установка моделей
ollama pull llama2      # Основная модель
ollama pull mistral     # Быстрая альтернатива
ollama pull codellama   # Для программирования
```

### OpenAI

```bash
# Создание .env файла
echo "OPENAI_API_KEY=your_api_key_here" > .env

# Установка зависимостей
pip install -r requirements.txt
```

### Vercel

```bash
# Развертывание на Vercel
vercel

# Настройка переменных окружения в Vercel Dashboard
OPENAI_API_KEY=your_api_key_here
```

## 📊 Сравнение версий

| Версия | Стоимость | Приватность | Скорость | Сложность |
|--------|-----------|-------------|----------|-----------|
| **Ollama** | Бесплатно | 100% | Зависит от железа | Простая |
| **OpenAI** | Платная | Нет | Быстрая | Средняя |
| **Vercel** | Бесплатно | Нет | Средняя | Простая |

## 🎯 Преимущества

### Ollama версия:
- ✅ **Полностью бесплатно**
- ✅ **100% приватность**
- ✅ **Работает без интернета**
- ✅ **Множество моделей**
- ✅ **Полная настройка**

### OpenAI версия:
- ✅ **Высокое качество**
- ✅ **Быстрая работа**
- ✅ **Простота использования**
- ✅ **Облачное развертывание**

### Vercel версия:
- ✅ **Быстрое развертывание**
- ✅ **Глобальный CDN**
- ✅ **SSL сертификаты**
- ✅ **Автоматические обновления**

## 🔍 Устранение неполадок

### Ollama проблемы:

```bash
# Сервис не запущен
ollama serve

# Модель не найдена
ollama pull llama2

# Недостаточно памяти
ollama pull llama2:7b  # Легкая версия
```

### OpenAI проблемы:

```bash
# API ключ не найден
echo "OPENAI_API_KEY=your_key" > .env

# Ошибки зависимостей
pip install -r requirements.txt --upgrade
```

### Общие проблемы:

```bash
# Очистка кэша
streamlit cache clear

# Перезапуск
python run_ollama.py
```

## 🚀 Развертывание

### Локально
```bash
python run_ollama.py
```

### Vercel
```bash
vercel --prod
```

### Docker
```bash
docker build -t sherlock-bot .
docker run -p 8501:8501 sherlock-bot
```

## 📚 Документация

- [📖 Полное руководство](README.md)
- [⚡ Быстрый старт](QUICKSTART.md)
- [🤖 Ollama руководство](OLLAMA_GUIDE.md)
- [🚀 Развертывание](DEPLOYMENT.md)
- [☁️ Vercel настройка](VERCEL_SETUP.md)
- [📱 Streamlit руководство](STREAMLIT_GUIDE.md)

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для новой функции
3. Внесите изменения
4. Создайте Pull Request

## 📄 Лицензия

MIT License - используйте свободно для любых целей.

## 🎉 Благодарности

- **Ollama** - за отличную платформу локальных AI
- **OpenAI** - за GPT модели
- **Streamlit** - за прекрасный веб-фреймворк
- **Vercel** - за простое развертывание

---

*"Элементарно, Ватсон! Теперь у нас есть AI-детектив для всех случаев жизни!" 🕵️‍♂️* 