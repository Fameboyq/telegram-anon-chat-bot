<div align="center">

# 💬 Telegram Anonymous Chat Bot

**Modern, fast, fully asynchronous Anonymous Chat Bot for Telegram powered by `aiogram 3.x` and `aiosqlite`.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![aiogram 3.x](https://img.shields.io/badge/aiogram-3.x-2CA5E0?logo=telegram&logoColor=white)](https://docs.aiogram.dev/)
[![SQLite](https://img.shields.io/badge/Database-aiosqlite-003B57?logo=sqlite&logoColor=white)](https://sqlite.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://docker.com)

[English Documentation](#-english-guide) • [Инструкция на русском](#-инструкция-на-русском)

</div>

---

## 🔍 Tags & Topics (Keywords)
`telegram-bot` `anon-chat` `anonymous-chat-bot` `aiogram3` `python-telegram-bot` `telegram-anonymous-chat` `aiogram` `telegram-bot-template` `anonymous-chat` `fameboyq`

---

## 🌟 Key Features / Возможности

* ⚡ **Full Async Engine:** High performance built on `aiogram 3.x` and `aiosqlite`.
* 🎯 **Smart Matching Queue:** Connects random users or matches by shared interests.
* 🚻 **Gender Filters:** Choose own gender and filter target companion gender.
* 📷 **Rich Media Forwarding:** Seamlessly transfers text, photos, videos, voice messages, video notes (circles), stickers, and documents without exposing usernames.
* ⭐ **Rating & Report System:** Feedback buttons (👍 / 👎) and anti-spam complaint triggers after each dialogue.
* 💎 **VIP & Premium Subscriptions:** Integrated Telegram Stars payment handlers.
* 🐳 **Docker & 1-Click Launch:** Ready-to-go `run.bat` for Windows and `Dockerfile` + `docker-compose.yml` for Linux servers.

---

## 🇺🇸 English Guide

### 🚀 Quick Start (Local)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Fameboyq/telegram-anon-chat-bot.git
   cd telegram-anon-chat-bot
   ```

2. **Configure Environment:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and paste your bot token obtained from [@BotFather](https://t.me/BotFather):
   ```env
   BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ADMIN_IDS=12345678
   DB_PATH=bot.db
   ```

3. **Install Dependencies & Run:**
   * **Windows:** Just double-click `run.bat`!
   * **Manual / Linux:**
     ```bash
     pip install -r requirements.txt
     python bot.py
     ```

### 🐳 Run with Docker

```bash
docker compose up -d --build
```

---

## 🇷🇺 Инструкция на русском

### 🚀 Быстрый запуск

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/Fameboyq/telegram-anon-chat-bot.git
   cd telegram-anon-chat-bot
   ```

2. **Настройка токена:**
   Скопируйте `.env.example` в `.env`:
   ```bash
   copy .env.example .env
   ```
   Откройте файл `.env` в блокноте и вставьте токен вашего бота от [@BotFather](https://t.me/BotFather):
   ```env
   BOT_TOKEN=ВАШ_ТОКЕН_ОТ_БОТФАЗЕРА
   ADMIN_IDS=ВАШ_ТЕЛЕГРАМ_АЙДИ
   DB_PATH=bot.db
   ```

3. **Запуск бота:**
   * **На Windows:** Дважды кликните по `run.bat`. Скрипт сам установит нужные библиотеки и запустит бота!
   * **На Linux / VPS:**
     ```bash
     pip install -r requirements.txt
     python bot.py
     ```

### ⚙️ Команды бота
* `/search` — Поиск собеседника
* `/next` — Завершить текущий диалог и сразу искать нового
* `/stop` — Завершить диалог
* `/interests` — Выбор интересов для поиска
* `/settings` — Настройки пола и профиля
* `/vip` — VIP статус и премиум фильтры

---

## 👤 Author
* **Fameboyq** - [GitHub](https://github.com/Fameboyq) • [Website](https://fameboyq.fun) • [Telegram](https://t.me/fameboyq)

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
