import asyncio
import os
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from playwright.async_api import async_playwright

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # e.g., "-1002117580257"

TIKTOK_URL = "https://www.tiktok.com/@yeti.solana"

async def fetch_stats():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await browser.new_page()
        await page.goto(TIKTOK_URL)
        # Wait for the stats to load
        await page.wait_for_timeout(5000)

        # Extract follower and like counts
        stats = await page.evaluate("""() => {
            const els = document.querySelectorAll("strong");
            const [followers, likes] = [els[0]?.innerText, els[2]?.innerText];
            return { followers, likes };
        }""")
        await browser.close()
        return stats["followers"], stats["likes"]

async def send_stats(bot: Bot):
    followers, likes = await fetch_stats()
    message = f"📊 TikTok Update:\n👥 Followers: {followers}\n❤️ Likes: {likes}"
    await bot.send_message(chat_id=CHAT_ID, text=message)

async def cmd_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    followers, likes = await fetch_stats()
    await update.message.reply_text(f"📊 TikTok Stats:\n👥 Followers: {followers}\n❤️ Likes: {likes}")

async def scheduled_loop(app):
    while True:
        await send_stats(app.bot)
        await asyncio.sleep(6 * 3600)  # 6 hours

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("tiktokstats", cmd_tiktok))
    asyncio.create_task(scheduled_loop(app))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
