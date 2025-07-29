#!/usr/bin/env python3
"""
Скрипт запуска Czech Tour Monitor Bot
"""

import asyncio
import sys
import logging

# Импортируем основной класс бота
from czech_tour_bot import CzechTourMonitor

def main():
    """Главная функция запуска"""
    print("🚀 Запуск Czech Tour Monitor Bot...")
    print("📋 Параметры мониторинга:")
    print("   💰 Максимум: 25,000 Kč")
    print("   📅 Дата: 8 сентября 2024")
    print("   ⏱️ Длительность: 6-7 дней")
    print("   👥 2 взрослых + 1 ребенок (2 года)")
    print("   🏖️ Отели у моря (до 200м)")
    print("   ⏰ Проверка каждый час")
    print()
    print("🌐 Мониторинг сайтов:")
    print("   • Čedok")
    print("   • Fischer")
    print("   • Eximtours")
    print("   • Blue Style")
    print("   • Invia")
    print()
    print("📱 Бот доступен: @Tetris_CZBot")
    print("=" * 50)
    
    # Создаем и запускаем бота
    bot_token = "7892612647:AAFWQlK5pcHx2olikmQkAjC2N7LQzOcRjMw"
    bot = CzechTourMonitor(bot_token)
    
    try:
        # Запускаем бота
        asyncio.run(bot.start_bot())
    except KeyboardInterrupt:
        print("\n⛔ Получен сигнал остановки (Ctrl+C)")
        print("🛑 Остановка бота...")
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
