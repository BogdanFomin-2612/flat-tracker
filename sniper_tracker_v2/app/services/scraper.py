import random
import logging
from typing import Optional, List, Dict, Any
from bs4 import BeautifulSoup
from curl_cffi.requests import AsyncSession

logger = logging.getLogger(__name__)

class RealEstateScraper:
    def __init__(self):
        # Пул прокси (в будущем сюда можно добавить строки "http://login:pass@ip:port")
        self.proxies = []
        
        # Mid-level стандарт: полная маскировка под реальный браузер Google Chrome (Windows)
        self.base_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "uk-UA,uk;q=0.9,ru;q=0.8,en-US;q=0.7,en;q=0.6",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }

    def _get_random_proxy(self) -> Optional[str]:
        """Возвращает случайный прокси из пула или None, если пул пуст."""
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    async def fetch_html(self, url: str) -> str:
        """Асинхронная загрузка страницы с ротацией прокси, маскировкой и жесткой сортировкой."""
        
        # ПРИНУДИТЕЛЬНО включаем сортировку "Самые новые", если её нет в ссылке
        if "search%5Border%5D=created_at%3Adesc" not in url and "search[order]=created_at:desc" not in url:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}search[order]=created_at:desc"

        proxy = self._get_random_proxy()
        proxies = {"http": proxy, "https": proxy} if proxy else None

        try:
            # OLX отдаёт 403 на TLS-отпечаток httpx, поэтому маскируемся под Chrome через curl_cffi.
            # Заголовки берёт сам профиль impersonate, свои только язык.
            async with AsyncSession(impersonate="chrome", proxies=proxies, timeout=15) as client:
                response = await client.get(
                    url,
                    headers={"Accept-Language": self.base_headers["Accept-Language"]},
                    allow_redirects=True,
                )
                if response.status_code >= 400:
                    logger.error(f"HTTP ошибка при загрузке {url} (прокси: {proxy}): {response.status_code}")
                    return ""
                return response.text

        except Exception as e:
            logger.error(f"Сетевая ошибка при загрузке {url} (прокси: {proxy}): {e}")
            return ""

    def extract_ads_data(self, html: str) -> List[Dict[str, Any]]:
        """Извлечение базовых данных объявлений со страницы списка."""
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        ads = []
        
        # Ищем карточки объявлений (селектор OLX)
        cards = soup.find_all('div', {'data-cy': 'l-card'})
        
        for card in cards:
            try:
                # OLX периодически меняет вёрстку: сначала data-testid, потом старые теги как запасной вариант
                title_elem = card.find(attrs={'data-testid': 'ad-card-title'}) or card.find(['h4', 'h6'])
                price_elem = card.find('p', {'data-testid': 'ad-price'})
                link_elem = card.find('a', {'data-testid': 'card-title-link'}) or card.find('a')
                
                if title_elem and price_elem and link_elem:
                    ad_url = link_elem.get('href')
                    if not ad_url.startswith('http'):
                        ad_url = f"https://www.olx.ua{ad_url}"
                        
                    ads.append({
                        "title": title_elem.text.strip(),
                        "price": price_elem.text.strip(),
                        "url": ad_url
                    })
            except Exception as e:
                logger.warning(f"Ошибка парсинга отдельной карточки: {e}")
                continue
                
        return ads

    async def fetch_ad_details(self, url: str) -> Dict[str, Any]:
        """Загрузка внутренней страницы объявления для получения деталей (комнаты, тип автора)."""
        details = {"rooms": 0, "is_owner": False}
        html = await self.fetch_html(url)
        
        if not html:
            return details
            
        soup = BeautifulSoup(html, 'html.parser')
        
        try:
            # Берём только блок параметров объявления: "Приватна особа" встречается и в JSON внутри <script>,
            # поэтому поиск по всей странице давал is_owner=True для любого объявления
            params_container = soup.find(attrs={'data-testid': 'ad-parameters-container'})
            params_list = params_container.find_all(['p', 'li']) if params_container else soup.find_all('li')

            # Проверка на собственника
            if any(p.get_text(strip=True) == "Приватна особа" for p in params_list):
                details["is_owner"] = True

            # Парсинг количества комнат из характеристик
            for param in params_list:
                text = param.text.lower()
                if "кількість кімнат:" in text or "количество комнат:" in text:
                    # Извлекаем первую цифру из строки
                    digits = [int(s) for s in text.split() if s.isdigit()]
                    if digits:
                        details["rooms"] = digits[0]
                    break
                    
        except Exception as e:
            logger.warning(f"Ошибка при парсинге деталей объявления {url}: {e}")
            
        return details