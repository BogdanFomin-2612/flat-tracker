import asyncio
import logging
import re
from datetime import datetime, timezone, timedelta

from app.core.celery_app import celery_app
from app.services.scraper import RealEstateScraper
from app.services.telegram import send_telegram_message
from app.core.database import async_session_maker, engine
from app.models.domain import SearchTask, ScrapedAd
from sqlalchemy import select
from sqlalchemy.orm import joinedload

logger = logging.getLogger(__name__)

async def process_active_tasks():
    try:
        scraper = RealEstateScraper()
        async with async_session_maker() as session:
            # 1. Загружаем все активные задачи
            result = await session.execute(
                select(SearchTask)
                .options(joinedload(SearchTask.owner))
                .where(SearchTask.is_active == True)
            )
            all_tasks = result.scalars().all()

            if not all_tasks:
                return

            now = datetime.now(timezone.utc)
            tasks_to_process = []

            # 2. Умный диспетчер: фильтруем задачи и блокируем их от дублирующих воркеров
            for task in all_tasks:
                if not getattr(task, 'last_checked', None):
                    tasks_to_process.append(task)
                    task.last_checked = datetime.now(timezone.utc)
                    session.add(task)
                    continue

                last_checked = task.last_checked
                if last_checked.tzinfo is None:
                    last_checked = last_checked.replace(tzinfo=timezone.utc)
                    
                interval = timedelta(minutes=task.check_interval_minutes)
                
                if now - last_checked >= interval:
                    tasks_to_process.append(task)
                    # СРАЗУ обновляем время, чтобы заблокировать задачу для воркера из следующей минуты
                    task.last_checked = datetime.now(timezone.utc)
                    session.add(task)

            if not tasks_to_process:
                logger.info("Ожидание. Нет задач с подошедшим интервалом проверки.")
                return

            # ФИКС ГОНКИ: Коммитим таймстемпы в базу ДО начала долгого парсинга!
            await session.commit()

            # 3. Парсинг только для тех задач, чья очередь подошла
            for task in tasks_to_process:
                html = await scraper.fetch_html(task.url)
                if not html:
                    continue
                
                ads = scraper.extract_ads_data(html)
                
                for ad_data in ads:
                    # Очистка и конвертация валюты
                    price_text = ad_data.get("price", "").lower()
                    price_digits = re.sub(r"[^\d]", "", price_text)
                    clean_price = int(price_digits) if price_digits else 0
                    
                    if clean_price > 0:
                        if "$" in price_text or "долар" in price_text:
                            clean_price *= 41  
                        elif "€" in price_text or "євро" in price_text or "евро" in price_text:
                            clean_price *= 45
                            
                    ext_id_match = re.search(r'ID([^.]+)\.html', ad_data.get("url", ""))
                    ext_id = ext_id_match.group(1) if ext_id_match else ad_data.get("url", "")[:30]
                    
                    # Жесткие фильтры по цене
                    if task.min_price or task.max_price:
                        if clean_price == 0:
                            continue 
                        if task.min_price and clean_price < task.min_price:
                            continue
                        if task.max_price and clean_price > task.max_price:
                            continue
                            
                    existing_ad = await session.execute(select(ScrapedAd).where(ScrapedAd.external_id == ext_id))
                    if existing_ad.scalars().first():
                        continue
                        
                    details = await scraper.fetch_ad_details(ad_data.get("url", ""))
                    await asyncio.sleep(1.5)
                    
                    # Жесткий фильтр комнат
                    if task.rooms and details.get("rooms", 0) > 0:
                        if details["rooms"] != task.rooms:
                            continue
                            
                    if task.owner_only and not details.get("is_owner"):
                        continue
                        
                    new_ad = ScrapedAd(
                        task_id=task.id,
                        external_id=ext_id,
                        title=ad_data.get("title", ""),
                        price=clean_price,
                        url=ad_data.get("url", "")
                    )
                    session.add(new_ad)
                    
                    # Отправка уведомления
                    if task.owner and task.owner.telegram_chat_id:
                        owner_badge = "👤 Собственник" if details.get("is_owner") else "🏢 Риелтор/Бизнес"
                        rooms_text = f"Комнат: {details['rooms']}" if details.get("rooms", 0) > 0 else "Комнаты не указаны"
                        
                        msg = (
                            f"🎯 <b>Новая цель: {task.title}</b>\n\n"
                            f"🏠 <b>{ad_data.get('title', '')}</b>\n"
                            f"💰 {ad_data.get('price', '')}\n"
                            f"📏 {rooms_text} | {owner_badge}\n\n"
                            f"🔗 <a href='{ad_data.get('url', '')}'>Перейти к объявлению</a>"
                        )
                        await send_telegram_message(task.owner.telegram_chat_id, msg)
            
            # 4. Сохраняем новые объявления в базу после окончания цикла
            await session.commit()
            
    finally:
        await engine.dispose()

@celery_app.task(name="check_new_apartments")
def check_new_apartments_task():
    asyncio.run(process_active_tasks())
    return "completed"