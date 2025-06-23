import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def setup_selenium(self):
        """Настройка Selenium для динамических сайтов"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            driver = webdriver.Chrome(
                ChromeDriverManager().install(),
                options=chrome_options
            )
            return driver
        except Exception as e:
            logger.error(f"Ошибка при настройке Selenium: {e}")
            return None

    def clean_text(self, text):
        """Очистка текста от лишних символов"""
        # Удаляем лишние пробелы и переносы строк
        text = re.sub(r'\s+', ' ', text)
        # Удаляем специальные символы
        text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)\[\]]', '', text)
        return text.strip()

    def extract_main_content(self, soup, url):
        """Извлечение основного контента страницы"""
        # Удаляем ненужные элементы
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Попытка найти основной контент
        main_selectors = [
            'main',
            '[role="main"]',
            '.main-content',
            '.content',
            '#content',
            '.post-content',
            '.article-content',
            '.entry-content'
        ]
        
        main_content = None
        for selector in main_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            # Если не найден основной контент, берем body
            main_content = soup.find('body') or soup
        
        return main_content

    def scrape_with_requests(self, url):
        """Скрапинг с помощью requests"""
        try:
            logger.info(f"Скрапинг {url} с помощью requests")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            main_content = self.extract_main_content(soup, url)
            
            # Извлекаем текст
            text = main_content.get_text()
            cleaned_text = self.clean_text(text)
            
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Ошибка при скрапинге {url}: {e}")
            return None

    def scrape_with_selenium(self, url):
        """Скрапинг с помощью Selenium для динамических сайтов"""
        driver = None
        try:
            logger.info(f"Скрапинг {url} с помощью Selenium")
            driver = self.setup_selenium()
            
            if not driver:
                return None
            
            driver.get(url)
            
            # Ждем загрузки страницы
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Дополнительное время для загрузки динамического контента
            time.sleep(3)
            
            # Получаем HTML
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            main_content = self.extract_main_content(soup, url)
            text = main_content.get_text()
            cleaned_text = self.clean_text(text)
            
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Ошибка при скрапинге {url} с Selenium: {e}")
            return None
        finally:
            if driver:
                driver.quit()

    def scrape_wikipedia(self, url):
        """Специализированный скрапинг для Wikipedia"""
        try:
            logger.info(f"Скрапинг Wikipedia: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Удаляем ненужные элементы Wikipedia
            for element in soup(['script', 'style', 'nav', '.mw-editsection', '.mw-references-wrap']):
                element.decompose()
            
            # Находим основной контент
            content = soup.find('div', {'id': 'mw-content-text'})
            if not content:
                return None
            
            # Извлекаем заголовок
            title = soup.find('h1', {'id': 'firstHeading'})
            title_text = title.get_text() if title else ""
            
            # Извлекаем текст
            paragraphs = content.find_all(['p', 'h2', 'h3', 'h4'])
            text_parts = [title_text] if title_text else []
            
            for p in paragraphs:
                text = p.get_text().strip()
                if text and len(text) > 50:  # Минимальная длина
                    text_parts.append(text)
            
            full_text = '\n\n'.join(text_parts)
            return self.clean_text(full_text)
            
        except Exception as e:
            logger.error(f"Ошибка при скрапинге Wikipedia {url}: {e}")
            return None

    def scrape_url(self, url):
        """Основной метод скрапинга"""
        parsed_url = urlparse(url)
        
        # Специальная обработка для Wikipedia
        if 'wikipedia.org' in parsed_url.netloc:
            content = self.scrape_wikipedia(url)
        else:
            # Сначала пробуем requests
            content = self.scrape_with_requests(url)
            
            # Если не получилось, пробуем Selenium
            if not content:
                content = self.scrape_with_selenium(url)
        
        if content:
            # Разбиваем на чанки
            chunks = self.split_text_into_chunks(content, 1000)
            return chunks
        else:
            return ["Не удалось извлечь контент с данного URL"]

    def split_text_into_chunks(self, text, chunk_size):
        """Разбивает текст на чанки"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            if current_size + len(word) + 1 > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = len(word)
            else:
                current_chunk.append(word)
                current_size += len(word) + 1
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

    def get_page_info(self, url):
        """Получение информации о странице"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = soup.find('title')
            title_text = title.get_text() if title else "Без заголовка"
            
            description = soup.find('meta', {'name': 'description'})
            desc_text = description.get('content') if description else ""
            
            return {
                'title': title_text,
                'description': desc_text,
                'url': url
            }
        except Exception as e:
            logger.error(f"Ошибка при получении информации о странице: {e}")
            return {
                'title': "Ошибка",
                'description': "",
                'url': url
            } 