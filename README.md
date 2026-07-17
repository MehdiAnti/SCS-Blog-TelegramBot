# SCS Blog - Telegram Bot

A lightweight Telegram bot that automatically monitors the official **SCS Software Blog**, detects newly published article, converts into Telegram Rich Messages, and delivers directly to Telegram channel.

---

# Features

- Automatically detects new SCS Blog post
- Fetches and parses the complete article
- Sends the original hero image before the article
- Converts Blogger HTML into Telegram Rich Message format
- Preserves article links and formatting

---

# How It Works

```
GET /check
        │
        ▼
Latest SCS Article
        │
        ▼
Already Posted?
     │        │
     │Yes     │No
     ▼        ▼
   Finish   Fetch Article
                 │
                 ▼
        Clean HTML
                 │
                 ▼
        Send Hero Image
                 │
                 ▼
      Send Rich Message
```

---

# Requirements

- Python 3.11+
- Stuff included in `requirements.txt`

---

# Installation

Clone the repository

```bash
git clone https://github.com/MehdiAnti/SCS-Blog-TelegramBot.git

cd SCS-Blog-TelegramBot
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
python main.py
```

---

# Environment Variables

```
BOT_TOKEN
ALLOWED_USER
CHANNEL_ID
POST_TO_CHANNEL (true/false)
CF_ACCOUNT_ID
CF_API_TOKEN (kv storage: write)
CF_NAMESPACE_ID
```
---

# Sending Flow

1. Hero image
2. Rich Message article
3. Save latest article to Cloudflare KV storage

---


# License

This project is licensed under the MIT License.

---

**Powered by**

- Python
- Flask
- Telegram Bot API
- Cloudflare Workers
- Cloudflare API
- Render Web Service

Special thanks to **SCS Software** for creating amazing games and maintaining their official blog.

Happy Trucking! 🚛
