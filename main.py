import asyncio
import logging
import aioschedule
import aiogram
import os

from parsing import get_articles_tds, get_articles_habr

logger = logging.getLogger(__name__)


async def sender(dp: aiogram.dispatcher.Dispatcher) -> None:
    habr_links = await get_articles_habr()
    tds_links = await get_articles_tds()

    links = habr_links + tds_links

    logging.info(f'За вчера собрано {len(links)} статей')

    for link in links:
        await dp.bot.send_message(367318262, f'<b>Дата:</b> {link.date}\n'
                                             f'<b>Рейтинг:</b> {link.rating}\n'
                                             f'<b>Статья:</b> {link.link}', parse_mode=aiogram.types.ParseMode.HTML)


async def scheduler(dp: aiogram.dispatcher.Dispatcher) -> None:
    aioschedule.every(1).days.at('04:00').do(sender, dp=dp)
    while True:
        await aioschedule.run_pending()


async def on_startup(dp: aiogram.dispatcher.Dispatcher) -> None:
    asyncio.create_task(scheduler(dp))


# Настройка логирования в stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s+3h - %(levelname)s - %(name)s - %(message)s",
)
bot = aiogram.Bot(token=os.environ.get('BOT_TOKEN'))
dp = aiogram.Dispatcher(bot)


if __name__ == '__main__':
    aiogram.executor.start_polling(dispatcher=dp, on_startup=on_startup)