import os
import logging
import asyncio
from datetime import datetime, timezone
import httpx
from sqlalchemy import select
from app.core.database import async_session_maker
from app.models.domain import User

logger = logging.getLogger(__name__)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def send_telegram_message(chat_id: int, text: str):
    if not BOT_TOKEN or not chat_id:
        logger.warning("Не задан BOT_TOKEN или chat_id. Уведомление не отправлено.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=10.0)
            if response.status_code != 200:
                logger.error(f"Ошибка Telegram API: {response.text}")
        except Exception as e:
            # Не логируем сам exception целиком: в нём может оказаться URL с токеном бота
            logger.error(f"Сбой соединения с Telegram: {type(e).__name__}")

async def link_telegram_account(chat_id: int, token: str):
    """Связывает Telegram chat_id с аккаунтом пользователя по токену."""
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.telegram_connect_token == token))
        user = result.scalars().first()

        expires_at = user.telegram_connect_token_expires_at if user else None
        if user and expires_at and expires_at > datetime.now(timezone.utc):
            user.telegram_chat_id = chat_id
            # Код одноразовый: после привязки он больше не работает
            user.telegram_connect_token = None
            user.telegram_connect_token_expires_at = None
            session.add(user)
            await session.commit()

            success_msg = "✅ <b>Успешно!</b> Ваш Telegram привязан к аккаунту.\nТеперь бот будет присылать уведомления о новых квартирах сюда."
            await send_telegram_message(chat_id, success_msg)
            logger.info(f"Аккаунт пользователя id={user.id} успешно привязан к Telegram.")
        else:
            error_msg = "❌ Ошибка: неверный или устаревший токен привязки. Пожалуйста, сгенерируйте новую ссылку в личном кабинете."
            await send_telegram_message(chat_id, error_msg)

async def start_telegram_polling():
    """Фоновый процесс для прослушивания входящих команд бота."""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не найден, бот не может принимать сообщения.")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    offset = 0

    logger.info("Служба Telegram-бота запущена (Long Polling)...")

    async with httpx.AsyncClient() as client:
        while True:
            try:
                response = await client.get(f"{url}?offset={offset}&timeout=30", timeout=35.0)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("result", []):
                        offset = item["update_id"] + 1

                        message = item.get("message", {})
                        text = message.get("text", "")
                        chat_id = message.get("chat", {}).get("id")

                        if text.startswith("/start "):
                            token = text.split(" ", 1)[1].strip()
                            await link_telegram_account(chat_id, token)
                        elif text == "/start":
                            await send_telegram_message(chat_id, "👋 Привет! Чтобы получать уведомления, перейдите в личный кабинет на сайте и нажмите кнопку «Подключить Telegram».")

            except Exception as e:
                logger.error(f"Ошибка при получении обновлений Telegram: {type(e).__name__}")
                await asyncio.sleep(5)
