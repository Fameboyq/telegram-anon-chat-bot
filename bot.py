import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, BotCommand, LabeledPrice, PreCheckoutQuery
from aiogram.filters import CommandStart, Command
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest

from config import BOT_TOKEN
import database as db
import keyboards as kb

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ----------------- СИСТЕМНЫЕ КОМАНДЫ ДЛЯ МЕНЮ ТЕЛЕГРАМ -----------------

async def set_bot_commands():
    commands = [
        BotCommand(command="search", description="поиск собеседника"),
        BotCommand(command="next", description="закончить и сразу искать нового"),
        BotCommand(command="stop", description="закончить разговор"),
        BotCommand(command="interests", description="выбрать интересы поиска"),
        BotCommand(command="pay", description="поиск по полу и премиум"),
        BotCommand(command="vip", description="стать VIP-пользователем"),
        BotCommand(command="link", description="отправить собеседнику ссылку на себя"),
        BotCommand(command="settings", description="изменить свой пол и настройки"),
        BotCommand(command="rules", description="ознакомиться с правилами"),
    ]
    await bot.set_my_commands(commands)

# ----------------- СТАРТ И ОПИСАНИЕ БОТА -----------------

WELCOME_INFO = (
    "👋 **Это бот для анонимного общения в Телеграме**\n\n"
    "Бот умеет пересылать сообщения, фото, видео, гифки, стикеры, аудиосообщения и видеосообщения.\n\n"
    "⚡ **Команды управления:**\n"
    "/search — поиск собеседника\n"
    "/next — закончить текущий диалог и сразу же искать нового собеседника\n"
    "/stop — закончить разговор с собеседником\n"
    "/interests — выбрать интересы поиска\n"
    "/pay — поиск по полу, оформление и управление премиумом\n"
    "/vip — стать VIP-пользователем\n"
    "/link — отправить собеседнику ссылку на вас в Телеграме\n"
    "/settings — изменить свой пол и другие настройки\n"
    "/rules — ознакомиться с правилами"
)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    await db.create_user(user_id, username)
    user = await db.get_user(user_id)

    if user["is_banned"]:
        await message.answer("🚫 Вы заблокированы за нарушение правил сообщества.")
        return

    if user["companion_id"]:
        await end_dialog(user_id, user["companion_id"], notify=True)

    if not user["gender"]:
        await message.answer(
            f"{WELCOME_INFO}\n\n"
            "⚠️ **Для продолжения укажите ваш пол:**",
            reply_markup=kb.gender_select_inline(),
            parse_mode="Markdown"
        )
        return

    await message.answer(
        f"{WELCOME_INFO}\n\n"
        f"Нажмите **«🔎 Найти собеседника»** или введите команду /search для начала!",
        reply_markup=kb.main_kb(),
        parse_mode="Markdown"
    )

# ----------------- ПОЛ И НАСТРОЙКИ (/settings) -----------------

@dp.message(Command("settings"))
@dp.message(F.text == "⚙️ Настройки")
async def cmd_settings(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user:
        return
    gender = "🚹 Парень" if user["gender"] == "M" else ("🚺 Девушка" if user["gender"] == "F" else "Не указан")
    target = "🚺 Только девушки" if user["target_gender"] == "F" else ("🚹 Только парни" if user["target_gender"] == "M" else "🎲 Любой")
    status = "💎 VIP" if user["is_vip"] else ("⭐️ Премиум" if user["is_premium"] else "Обычный")

    text = (
        f"⚙️ **Настройки профиля:**\n\n"
        f"• Ваш пол: **{gender}**\n"
        f"• Поиск по полу: **{target}**\n"
        f"• Статус: **{status}**\n"
        f"• Репутация: 👍 {user['likes']} | 👎 {user['dislikes']}\n"
        f"• Всего диалогов: {user['total_chats']}\n\n"
        f"Выберите, что хотите изменить:"
    )
    await message.answer(text, reply_markup=kb.gender_select_inline(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("set_gender_"))
async def cb_set_gender(callback: CallbackQuery):
    gender = callback.data.split("_")[-1]
    await db.update_user(callback.from_user.id, gender=gender)
    await callback.message.edit_text(
        f"✅ Ваш пол установлен: {'🚹 Парень' if gender == 'M' else '🚺 Девушка'}.\n\n"
        f"Кого вы хотите искать в первую очередь?",
        reply_markup=kb.target_gender_inline()
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("target_"))
async def cb_target_gender(callback: CallbackQuery):
    target = callback.data.split("_")[-1]
    user = await db.get_user(callback.from_user.id)

    # Фильтр только на девушек доступен премиум / VIP
    if target == "F" and not (user["is_premium"] or user["is_vip"]):
        await callback.answer("🔒 Поиск только девушек доступен в Премиуме (/pay)!", show_alert=True)
        return

    await db.update_user(callback.from_user.id, target_gender=target)
    label = "🚺 Только девушек" if target == "F" else ("🚹 Только парней" if target == "M" else "🎲 Кого угодно")
    await callback.message.delete()
    await callback.message.answer(
        f"✅ Поиск по полу обновлен: **{label}**.\n\n"
        f"Нажмите **«🔎 Найти собеседника»** для начала общения!",
        reply_markup=kb.main_kb(),
        parse_mode="Markdown"
    )
    await callback.answer()

# ----------------- ИНТЕРЕСЫ (/interests — ФОТО 2) -----------------

@dp.message(Command("interests"))
@dp.message(F.text == "📖 Интересы")
async def cmd_interests(message: Message):
    user = await db.get_user(message.from_user.id)
    selected = [i.strip() for i in (user["interests"] or "").split(",") if i.strip()]
    text = (
        "Мы попытаемся соединить вас с собеседниками, которые выбрали похожие интересы.\n\n"
        "Выберите ваши интересы:"
    )
    await message.answer(text, reply_markup=kb.interests_inline(selected))

@dp.callback_query(F.data.startswith("int_"))
async def cb_toggle_interest(callback: CallbackQuery):
    idx = int(callback.data.split("_")[1])
    interest_name = db.ALL_INTERESTS[idx]
    new_interests = await db.toggle_interest(callback.from_user.id, interest_name)
    await callback.message.edit_reply_markup(reply_markup=kb.interests_inline(new_interests))
    await callback.answer()

@dp.callback_query(F.data == "reset_interests")
async def cb_reset_interests(callback: CallbackQuery):
    await db.clear_interests(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=kb.interests_inline([]))
    await callback.answer("Интересы сброшены!", show_alert=False)

# ----------------- ОПЛАТА TELEGRAM STARS (/pay, /vip — ФОТО 3) -----------------

PREMIUM_TEXT = (
    "Преимущества премиум-подписки:\n\n"
    "📌 *Поиск по полу*\n"
    "👩‍🦰 Премиум пользователи могут искать только девушек или только парней\n\n"
    "📌 *Звонки и видеозвонки*\n"
    "📞 Премиум пользователи могут совершать аудио и видеозвонки своим собеседникам через бота. Подробнее в команде /call\n\n"
    "📌 *Безлимитное общение*\n"
    "♾ Премиум пользователи не могут получить ограничение на количество чатов в день\n\n"
    "📌 *Отсутствие рекламы*\n"
    "📲 Мы не показываем рекламу премиум пользователям\n\n"
    "📌 *Поддержка чата*\n"
    "🎁 Чем больше вы нас поддерживаете, тем больше новых функций мы внедрим, будем лучше модерировать чат и покупать больше рекламы для увеличения количества собеседников\n\n"
    "💎 Если вы хотите стать не просто премиум-пользователем, а уникальным VIP-собеседником, переходите за подробностями по команде /vip\n\n"
    "Выберите продолжительность премиума и удобный способ оплаты ниже:"
)

@dp.message(Command("pay"))
@dp.message(Command("vip"))
@dp.message(F.text == "💎 Премиум / VIP")
async def cmd_pay(message: Message):
    await message.answer(PREMIUM_TEXT, reply_markup=kb.premium_pay_inline(), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("buy_stars_"))
async def cb_buy_stars(callback: CallbackQuery):
    tariff = callback.data.split("_")[-1] # 7, 30, 365, vip

    tariffs_info = {
        "7": ("Премиум на 7 дней", "Поиск по полу, безлимитное общение и приоритет в очереди на 7 дней", 250),
        "30": ("Премиум на 1 месяц", "Поиск по полу, безлимитное общение и приоритет в очереди на 30 дней", 350),
        "365": ("Премиум на 1 год", "Поиск по полу, безлимитное общение и максимальный приоритет на 1 год", 1500),
        "vip": ("💎 VIP Статус навсегда", "Вечный VIP-статус: поиск по полу, выделение в чате и наивысший приоритет", 2500)
    }

    if tariff not in tariffs_info:
        await callback.answer("Тариф не найден", show_alert=True)
        return

    title, desc, stars_amount = tariffs_info[tariff]

    # Нативный инвойс Telegram Stars (валюта XTR)
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=title,
        description=desc,
        payload=f"sub_{tariff}",
        currency="XTR",
        prices=[LabeledPrice(label=title, amount=stars_amount)]
    )
    await callback.answer()

@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query: PreCheckoutQuery):
    # Подтверждаем готовность принять платёж
    await pre_checkout_query.answer(ok=True)

@dp.message(F.successful_payment)
async def process_successful_payment(message: Message):
    payload = message.successful_payment.invoice_payload
    user_id = message.from_user.id

    days_map = {
        "sub_7": 7,
        "sub_30": 30,
        "sub_365": 365
    }

    if payload == "sub_vip":
        await db.grant_subscription(user_id, is_vip=True)
        text = (
            "🎉 **Оплата 2500 ⭐️ успешно завершена!**\n\n"
            "Вам навсегда присвоен статус **💎 VIP**!\n"
            "Теперь вы можете искать только девушек через команду /settings, а ваши заявки на поиск подбираются мгновенно."
        )
    else:
        days = days_map.get(payload, 30)
        await db.grant_subscription(user_id, days=days, is_vip=False)
        text = (
            f"🎉 **Оплата успешно завершена!**\n\n"
            f"Вам начислен статус **⭐️ Премиум** на **{days} дней**!\n"
            f"Вам доступен поиск по полу в /settings и сняты любые лимиты на общение."
        )

    await message.answer(text, reply_markup=kb.main_kb(), parse_mode="Markdown")

# ----------------- ПРАВИЛА (/rules) -----------------

@dp.message(Command("rules"))
@dp.message(F.text == "📜 Правила")
async def cmd_rules(message: Message):
    rules_text = (
        "📜 **Правила Анонимного Чата:**\n\n"
        "1. Запрещена публикация любого контента с несовершеннолетними (автоматический бан).\n"
        "2. Запрещен спам, реклама каналов, продажа запрещенных веществ и услуг.\n"
        "3. Оскорбления и неадекватное поведение наказываются баном по жалобам собеседников.\n"
        "4. Все диалоги строго анонимны, пока вы сами не решите отправить ссылку через команду /link."
    )
    await message.answer(rules_text, reply_markup=kb.main_kb(), parse_mode="Markdown")

# ----------------- ПОДЕЛИТЬСЯ ССЫЛКОЙ (/link) -----------------

@dp.message(Command("link"))
@dp.message(F.text == "🔗 Отправить ссылку на себя")
async def cmd_link(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or not user["companion_id"]:
        await message.answer("Вы сейчас не общаетесь ни с кем. Команда доступна только во время диалога!", reply_markup=kb.main_kb())
        return

    comp_id = user["companion_id"]
    from_user = message.from_user
    if from_user.username:
        link_text = f"@{from_user.username}"
        msg = f"🔗 **Собеседник открыл свой профиль:** {link_text}"
    else:
        msg = f"🔗 **Собеседник открыл свой профиль:** [Открыть профиль в Telegram](tg://user?id={from_user.id})"

    try:
        await bot.send_message(comp_id, msg, parse_mode="Markdown")
        await message.answer("✅ Ссылка на ваш профиль отправлена собеседнику!")
    except Exception:
        await message.answer("⚠️ Не удалось отправить ссылку собеседнику.")

# ----------------- ПОИСК И МАТЧИНГ (/search, /next) -----------------

@dp.message(Command("search"))
@dp.message(F.text == "🔎 Найти собеседника")
@dp.message(Command("next"))
@dp.message(F.text == "➡️ Следующий")
async def handle_search(message: Message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    if not user or user["is_banned"]:
        return

    # Завершаем текущий диалог
    if user["companion_id"]:
        await end_dialog(user_id, user["companion_id"], notify=True)

    await db.update_user(user_id, state="searching")
    await message.answer("🔍 Ищем подходящего собеседника...", reply_markup=kb.search_kb())

    user_interests = [i.strip() for i in (user["interests"] or "").split(",") if i.strip()]
    companion = await db.find_companion(user_id, user["gender"], user["target_gender"], user_interests)

    if companion:
        comp_id = companion["user_id"]
        await db.connect_users(user_id, comp_id)

        user_info = "🚹 Парень" if user["gender"] == "M" else "🚺 Девушка"
        comp_info = "🚹 Парень" if companion["gender"] == "M" else "🚺 Девушка"

        # Проверяем общие интересы
        comp_interests = [i.strip() for i in (companion["interests"] or "").split(",") if i.strip()]
        common = set(user_interests).intersection(set(comp_interests))
        common_text = f"\n🎯 Общие интересы: {', '.join(common)}" if common else ""

        start_msg_comp = (
            f"🎉 **Собеседник найден!**\n"
            f"Перед вами: {comp_info}{common_text}\n\n"
            f"/next — искать другого собеседника\n"
            f"/stop — завершить диалог\n"
            f"/link — отправить ссылку на себя"
        )
        start_msg_user = (
            f"🎉 **Собеседник найден!**\n"
            f"Перед вами: {user_info}{common_text}\n\n"
            f"/next — искать другого собеседника\n"
            f"/stop — завершить диалог\n"
            f"/link — отправить ссылку на себя"
        )

        await message.answer(start_msg_comp, reply_markup=kb.chat_kb(), parse_mode="Markdown")
        try:
            await bot.send_message(comp_id, start_msg_user, reply_markup=kb.chat_kb(), parse_mode="Markdown")
        except Exception:
            await db.disconnect_users(user_id, comp_id)
            await message.answer("Собеседник покинул чат. Ищем другого...")
            await handle_search(message)

@dp.message(F.text == "❌ Отменить поиск")
async def handle_cancel_search(message: Message):
    user_id = message.from_user.id
    await db.update_user(user_id, state="idle")
    await message.answer("Поиск остановлен.", reply_markup=kb.main_kb())

# ----------------- ЗАВЕРШЕНИЕ ДИАЛОГА И ПЛАШКА ОТЗЫВА (ФОТО 1) -----------------

FEEDBACK_TEXT = (
    "Если хотите, оставьте мнение о вашем собеседнике. Это поможет находить вам подходящих собеседников\n\n"
    "⚠️ Если ваш собеседник неадекватно общался или нарушал правила чата, вы можете на него пожаловаться, используя кнопки ниже."
)

async def end_dialog(u1: int, u2: int, notify: bool = True):
    await db.disconnect_users(u1, u2)
    # Отправляем плашку оценки u1 о u2
    try:
        await bot.send_message(u1, FEEDBACK_TEXT, reply_markup=kb.end_dialog_feedback_inline(u2))
    except Exception:
        pass
    # Отправляем плашку u2 о u1
    if notify and u2:
        try:
            await bot.send_message(u2, "Диалог завершен собеседником.\n\n" + FEEDBACK_TEXT, reply_markup=kb.end_dialog_feedback_inline(u1))
        except Exception:
            pass

@dp.message(Command("stop"))
@dp.message(F.text == "🛑 Завершить")
async def handle_stop(message: Message):
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    if not user or not user["companion_id"]:
        await message.answer("Вы сейчас не в диалоге.", reply_markup=kb.main_kb())
        return

    comp_id = user["companion_id"]
    await end_dialog(user_id, comp_id, notify=True)

# ----------------- ОБРАБОТКА ОЦЕНОК И ЖАЛОБ (ФОТО 1) -----------------

@dp.callback_query(F.data.startswith("rate_like_"))
async def cb_rate_like(callback: CallbackQuery):
    target_id = int(callback.data.split("_")[-1])
    await db.rate_user(target_id, is_like=True)
    await callback.message.edit_text("Спасибо за отзыв! Ваша положительная оценка учтена 👍", reply_markup=None)
    await callback.answer()

@dp.callback_query(F.data.startswith("rate_dislike_"))
async def cb_rate_dislike(callback: CallbackQuery):
    target_id = int(callback.data.split("_")[-1])
    await db.rate_user(target_id, is_like=False)
    await callback.message.edit_text("Спасибо за отзыв! Мы учтем это при дальнейшем подборе собеседников 👎", reply_markup=None)
    await callback.answer()

@dp.callback_query(F.data.startswith("rep_"))
async def cb_report(callback: CallbackQuery):
    parts = callback.data.split("_")
    reason_code = parts[1] # spam, lewd, minor, other
    target_id = int(parts[2])

    reasons_map = {
        "spam": "Спам и реклама",
        "lewd": "Пошлый собеседник",
        "minor": "Несовершеннолетний",
        "other": "Другая жалоба"
    }
    reason_title = reasons_map.get(reason_code, "Нарушение")
    await db.report_user(target_id, reason=reason_title)

    await callback.message.edit_text(f"🚨 Ваша жалоба на тему «{reason_title}» отправлена модераторам. Спасибо за помощь сообществу!", reply_markup=None)
    await callback.answer("Жалоба принята!", show_alert=True)

@dp.message(F.text == "⚠️ Пожаловаться")
async def handle_report_btn(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or not user["companion_id"]:
        await message.answer("Сейчас нет активного собеседника для жалобы.", reply_markup=kb.main_kb())
        return
    comp_id = user["companion_id"]
    await end_dialog(message.from_user.id, comp_id, notify=True)

# ----------------- АНОНИМНАЯ ПЕРЕСЫЛКА ВСЕХ ТИПОВ СООБЩЕНИЙ -----------------

@dp.message()
async def forward_any_message(message: Message):
    user = await db.get_user(message.from_user.id)
    if not user or not user["companion_id"]:
        await message.answer(
            "Вы сейчас ни с кем не общаетесь.\nНажмите **«🔎 Найти собеседника»** или отправьте /search!",
            reply_markup=kb.main_kb(),
            parse_mode="Markdown"
        )
        return

    comp_id = user["companion_id"]
    try:
        # Анонимное копирование любого типа контента (текст, фото, видео, кружочки, ГС, стикеры, документы)
        await bot.copy_message(
            chat_id=comp_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
    except TelegramForbiddenError:
        await end_dialog(message.from_user.id, comp_id, notify=False)
        await message.answer("Собеседник покинул чат. Нажмите /search для нового поиска.", reply_markup=kb.main_kb())
    except TelegramBadRequest as e:
        logging.error(f"Copy error: {e}")
        await message.answer("⚠️ Это сообщение не удалось передать собеседнику.")

# ----------------- ТОЧКА ВХОДА -----------------

async def main():
    await db.init_db()
    await set_bot_commands()
    print(">>> Анонимный Чат 18+ с нативной оплатой Telegram Stars запущен! <<<")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
