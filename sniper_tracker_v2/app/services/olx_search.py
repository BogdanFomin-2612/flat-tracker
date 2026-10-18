from typing import Optional
from urllib.parse import urlencode

OLX_BASE = "https://www.olx.ua/uk/nedvizhimost/kvartiry"

# Тип сделки -> (раздел OLX, название для интерфейса)
DEAL_TYPES = {
    "rent": ("dolgosrochnaya-arenda-kvartir", "Долгосрочная аренда"),
    "sale": ("prodazha-kvartir", "Продажа"),
}

# Слаги городов OLX (проверены запросом: каждый отдаёт 200, несуществующий — 404)
CITIES = {
    "kiev": "Киев",
    "kharkov": "Харьков",
    "odessa": "Одесса",
    "dnepr": "Днепр",
    "lvov": "Львов",
    "zaporozhe": "Запорожье",
    "vinnitsa": "Винница",
    "poltava": "Полтава",
    "ivano-frankovsk": "Ивано-Франковск",
    "ternopol": "Тернополь",
    "uzhgorod": "Ужгород",
    "chernigov": "Чернигов",
    "cherkassy": "Черкассы",
    "zhitomir": "Житомир",
    "rovno": "Ровно",
    "lutsk": "Луцк",
    "sumy": "Сумы",
    "khmelnitskiy": "Хмельницкий",
    "chernovtsy": "Черновцы",
    "kropivnitskiy": "Кропивницкий",
    "nikolaev": "Николаев",
    "kherson": "Херсон",
    "kremenchug": "Кременчуг",
    "mukachevo": "Мукачево",
    "kamenets-podolskiy": "Каменец-Подольский",
    "belaya-tserkov": "Белая Церковь",
    "irpen": "Ирпень",
    "bucha": "Буча",
    "brovary": "Бровары",
    "vishnevoe": "Вишнёвое",
}

# Количество комнат -> значение фильтра OLX
ROOMS = {
    1: "odnokomnatnye",
    2: "dvuhkomnatnye",
    3: "trehkomnatnye",
    4: "chetyrehkomnatnye",
    5: "pyatikomnatnye",
}


def build_search_url(
    deal_type: str,
    city: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    rooms: Optional[int] = None,
    owner_only: bool = False,
) -> str:
    """Собирает ссылку на поиск OLX. Фильтры передаются в саму ссылку,
    чтобы OLX отдавал уже отобранные объявления, а не первые 50 подряд.
    Без города ищет по всей Украине."""
    path = f"{OLX_BASE}/{DEAL_TYPES[deal_type][0]}/"
    if city:
        path += f"{city}/"

    params = {"search[order]": "created_at:desc"}
    if min_price:
        params["search[filter_float_price:from]"] = min_price
    if max_price:
        params["search[filter_float_price:to]"] = max_price
    if rooms in ROOMS:
        params["search[filter_enum_number_of_rooms_string][0]"] = ROOMS[rooms]
    if owner_only:
        params["search[private_business]"] = "private"

    return f"{path}?{urlencode(params)}"
