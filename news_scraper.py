import httpx
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin

# Настройка логгирования
logger = logging.getLogger(__name__)

async def scrape_article(url: str) -> dict | None:
    """
    Собирает данные статьи (заголовок, текст, изображение) с указанного URL.
    """
    logger.info(f"Начинаю сбор данных со страницы: {url}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True, timeout=30.0)
            response.raise_for_status()
    except httpx.RequestError as e:
        logger.error(f"Ошибка при запросе к {url}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # --- Поиск элементов ---
    # Селекторы основаны на анализе HTML-структуры сайта от 23.08.2025

    # Поиск заголовка
    title_element = soup.select_one('div.detail-title h3')
    title = title_element.get_text(strip=True) if title_element else "Заголовок не найден"

    # Поиск основного контейнера статьи
    article_container = soup.find('div', class_='news-detail')
    if not article_container:
        logger.error("Не удалось найти основной контейнер статьи (div.news-detail).")
        return None

    # Поиск изображения
    image_element = article_container.select_one('div.detail-img img.detail_picture')
    image_url = None
    if image_element and image_element.get('src'):
        image_url = urljoin(url, image_element['src'])

    # Поиск текста статьи
    # Находим все div'ы со стилем text-align: justify внутри основного контейнера
    body_divs = article_container.find_all('div', style="text-align: justify;")
    body = "\n".join([div.get_text(strip=True) for div in body_divs if div.get_text(strip=True)])

    if not title or not body:
        logger.error("Не удалось извлечь заголовок или текст статьи.")
        return None

    logger.info(f"Сбор данных завершен. Заголовок: {title}")

    return {
        "title": title,
        "body": body,
        "image_url": image_url
    }
