# Настройка API ключа Hugging Face

## 🔑 Как получить API ключ Hugging Face

### 1. Регистрация на Hugging Face
1. Перейдите на [huggingface.co](https://huggingface.co)
2. Нажмите "Sign Up" и создайте аккаунт
3. Подтвердите email

### 2. Получение API ключа
1. Войдите в свой аккаунт
2. Перейдите в [Settings -> Access Tokens](https://huggingface.co/settings/tokens)
3. Нажмите "New token"
4. Выберите "Read" для базового доступа
5. Введите название токена (например, "Sherlock Holmes Bot")
6. Нажмите "Generate token"
7. **Скопируйте токен** (он показывается только один раз!)

### 3. Настройка в проекте
1. Откройте файл `.env` в корне проекта
2. Замените `your_huggingface_api_key_here` на ваш реальный токен:

```env
HUGGINGFACE_API_KEY=hf_your_actual_token_here
```

### 4. Перезапуск сервера
После добавления API ключа перезапустите сервер:

```bash
python app_huggingface_simple.py
```

## 🚀 Альтернативные варианты

### Вариант 1: Использовать без API ключа (ограниченная функциональность)
Если у вас нет API ключа, бот все равно будет работать, но с ограниченными возможностями.

### Вариант 2: Использовать локальные модели
Можно настроить использование локальных моделей через Ollama или другие решения.

## 🔒 Безопасность
- **Никогда не коммитьте** файл `.env` в git
- Файл `.env` уже добавлен в `.gitignore`
- Храните API ключи в безопасном месте

## 📝 Пример файла .env
```env
# Hugging Face API Key
HUGGINGFACE_API_KEY=hf_your_actual_token_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True

# Other Configuration
LOG_LEVEL=INFO
```

## 🆘 Если возникли проблемы
1. Проверьте, что токен скопирован полностью
2. Убедитесь, что в файле .env нет лишних пробелов
3. Проверьте права доступа к файлу .env
4. Перезапустите сервер после изменения .env 