"""
Авто-постер для Telegram канала
Генерирует посты через DeepSeek AI и публикует по расписанию
Работает без VPN из России
"""

import os
import time
import random
import requests
import schedule
from datetime import datetime
from openai import OpenAI  # DeepSeek совместим с OpenAI SDK

# Загружаем .env локально (на Railway переменные задаются в панели)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ==================== НАСТРОЙКИ ====================
TG_BOT_TOKEN  = os.getenv("TG_BOT_TOKEN", "")
TG_CHANNEL_ID = os.getenv("TG_CHANNEL_ID", "")
DEEPSEEK_KEY  = os.getenv("DEEPSEEK_KEY", "")
POSTS_PER_DAY = int(os.getenv("POSTS_PER_DAY", "4"))
# ====================================================

client = None  # инициализируется после проверки конфига

TOPICS = [
    "психология и поведение людей",
    "деньги и богатство",
    "неожиданные факты о природе",
    "лайфхаки для жизни",
    "интересные факты об истории",
    "наука простыми словами",
    "интересные факты о еде",
    "странные законы разных стран",
    "рекорды и удивительные достижения",
    "факты о мозге и памяти",
    "факты о космосе",
    "неочевидные факты о технологиях",
]

FORMATS = [
    "интересный факт с объяснением",
    "топ-3 удивительных факта",
    "\"а знаешь ли ты, что...\" с крутым фактом",
    "лайфхак который реально работает",
    "факт который сложно в это поверить",
    "\"это изменит твой взгляд на...\" с объяснением",
]

SYSTEM_PROMPT = """Ты контент-менеджер популярного Telegram канала "Мозгоёб".
Пиши короткие вирусные посты на русском языке.
Правила:
- Длина: 100-250 слов
- Стиль: живой, разговорный, без воды и канцелярщины
- Добавляй 2-3 эмодзи в пост (не переусердствуй)
- В конце добавь 3-4 хэштега
- НЕ добавляй заголовок вида "Пост:" или "Факт:"
- Пиши так, чтобы хотелось поделиться с другом"""


def generate_post() -> str:
    topic = random.choice(TOPICS)
    fmt = random.choice(FORMATS)
    prompt = f"Напиши {fmt} на тему: {topic}"

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
        max_tokens=500,
        temperature=0.9,
    )
    return response.choices[0].message.content


def send_to_channel(text: str) -> bool:
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    r = requests.post(url, json={
        "chat_id": TG_CHANNEL_ID,
        "text": text,
    }, timeout=10)

    if r.status_code == 200:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Пост опубликован")
        return True
    else:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Telegram ошибка: {r.text}")
        return False


def post_job():
    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 Генерирую пост...")
        text = generate_post()
        send_to_channel(text)
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️  Ошибка: {e}")


def check_config() -> bool:
    errors = []
    if not TG_BOT_TOKEN:  errors.append("❌ TG_BOT_TOKEN не задан")
    if not TG_CHANNEL_ID: errors.append("❌ TG_CHANNEL_ID не задан")
    if not DEEPSEEK_KEY:  errors.append("❌ DEEPSEEK_KEY не задан")
    if errors:
        print("\n".join(errors))
        print("\n👉 Заполни .env файл и перезапусти")
        return False
    return True


def main():
    global client

    print("=" * 50)
    print("   🚀 Telegram Авто-постер [DeepSeek]")
    print("=" * 50)

    if not check_config():
        return

    client = OpenAI(
        api_key=DEEPSEEK_KEY,
        base_url="https://api.deepseek.com",
    )

    # Сразу публикуем при старте
    post_job()

    # Расписание: равномерно с 9:00 до 23:00
    interval = 14 / max(POSTS_PER_DAY - 1, 1)
    times = [f"{int(9 + i * interval):02d}:{random.randint(0, 59):02d}"
             for i in range(POSTS_PER_DAY)]

    for t in times:
        schedule.every().day.at(t).do(post_job)
        print(f"   📅 {t}")

    print(f"\n✅ Бот работает. {POSTS_PER_DAY} постов/день. Ctrl+C — стоп.\n")

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
