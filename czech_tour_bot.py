import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import aiohttp
import re
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

@dataclass
class TourOffer:
    """Структура предложения тура"""
    title: str
    destination: str
    price: int  # в кронах
    currency: str
    date_start: str
    date_end: str
    duration: int
    hotel_name: str
    hotel_stars: Optional[int]
    beach_distance: Optional[str]
    meals: str
    operator: str
    url: str
    last_seen: datetime

class CzechTourMonitor:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.app = Application.builder().token(bot_token).build()
        
        # Параметры поиска (под ваши требования)
        self.search_params = {
            'max_price': 25000,  # кроны
            'departure_date': '2024-09-08',
            'duration_min': 6,
            'duration_max': 7,
            'adults': 2,
            'children_age_2': 1,
            'max_beach_distance': 200,  # метры
            'departure_city': 'Praha'
        }
        
        # Найденные туры (для предотвращения дубликатов)
        self.found_tours: Dict[str, TourOffer] = {}
        self.user_chat_id: Optional[int] = None
        self.monitoring_active = True
        
        # URL турфирм
        self.tour_operators = {
            'cedok': 'https://www.cedok.cz',
            'fischer': 'https://www.fischer.cz', 
            'eximtours': 'https://www.eximtours.cz',
            'blue_style': 'https://www.blue-style.cz',
            'invia': 'https://www.invia.cz'
        }
        
        # Добавляем обработчики команд
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("settings", self.settings_command))
        self.app.add_handler(CommandHandler("found_tours", self.found_tours_command))
        self.app.add_handler(CallbackQueryHandler(self.button_callback))

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Запуск бота"""
        self.user_chat_id = update.effective_chat.id
        
        welcome_text = f"""
🏖️ Добро пожаловать в монитор туров по Чехии!

📋 Настройки поиска:
💰 Максимальная цена: {self.search_params['max_price']:,} Kč
📅 Дата вылета: {self.search_params['departure_date']}
⏱️ Длительность: {self.search_params['duration_min']}-{self.search_params['duration_max']} дней
👥 Взрослые: {self.search_params['adults']}, дети 2 лет: {self.search_params['children_age_2']}
🏖️ Расстояние до пляжа: до {self.search_params['max_beach_distance']}м
✈️ Вылет из: {self.search_params['departure_city']}

🔍 Мониторинг сайтов:
• Čedok
• Fischer 
• Eximtours
• Blue Style
• Invia

⏰ Проверка каждый час
🚀 Мониторинг запущен!

Команды:
/status - статус мониторинга
/settings - изменить параметры поиска
/found_tours - показать найденные туры
        """
        
        await update.message.reply_text(welcome_text)
        
        # Запускаем мониторинг
        if not hasattr(self, 'monitoring_task'):
            self.monitoring_task = asyncio
