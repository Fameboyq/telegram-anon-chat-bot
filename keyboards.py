from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database import ALL_INTERESTS

def main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔎 Найти собеседника")],
            [KeyboardButton(text="📖 Интересы"), KeyboardButton(text="💎 Премиум / VIP")],
            [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="📜 Правила")]
        ],
        resize_keyboard=True
    )

def chat_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➡️ Следующий"), KeyboardButton(text="🛑 Завершить")],
            [KeyboardButton(text="🔗 Отправить ссылку на себя"), KeyboardButton(text="⚠️ Пожаловаться")]
        ],
        resize_keyboard=True
    )

def search_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Отменить поиск")]
        ],
        resize_keyboard=True
    )

# 1. ПЛАШКА ОКОНЧАНИЯ ДИАЛОГА (ФОТО 1)
def end_dialog_feedback_inline(target_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👍", callback_data=f"rate_like_{target_id}"),
                InlineKeyboardButton(text="👎", callback_data=f"rate_dislike_{target_id}")
            ],
            [
                InlineKeyboardButton(text="🗂 Спам и реклама", callback_data=f"rep_spam_{target_id}")
            ],
            [
                InlineKeyboardButton(text="❌ Пошлый собеседник", callback_data=f"rep_lewd_{target_id}")
            ],
            [
                InlineKeyboardButton(text="🔞 Несовершеннолетний", callback_data=f"rep_minor_{target_id}")
            ],
            [
                InlineKeyboardButton(text="⚠️ Другая жалоба →", callback_data=f"rep_other_{target_id}")
            ]
        ]
    )

# 2. ВЫБОР ИНТЕРЕСОВ (ФОТО 2)
def interests_inline(selected_interests: list):
    buttons = []
    for i in range(0, len(ALL_INTERESTS), 2):
        row = []
        name1 = ALL_INTERESTS[i]
        icon1 = "✅ " if name1 in selected_interests else ""
        row.append(InlineKeyboardButton(text=f"{icon1}{name1}", callback_data=f"int_{i}"))

        if i + 1 < len(ALL_INTERESTS):
            name2 = ALL_INTERESTS[i + 1]
            icon2 = "✅ " if name2 in selected_interests else ""
            row.append(InlineKeyboardButton(text=f"{icon2}{name2}", callback_data=f"int_{i+1}"))
        buttons.append(row)

    buttons.append([InlineKeyboardButton(text="❌ Сбросить интересы", callback_data="reset_interests")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# 3. ТАРИФЫ ПРЕМИУМ И VIP (ФОТО 3)
def premium_pay_inline():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="7 дней за 250 ⭐️ / 299₽ / $2.99", callback_data="buy_stars_7")],
            [InlineKeyboardButton(text="1 месяц за 350 ⭐️ / 499₽ / $4.99", callback_data="buy_stars_30")],
            [InlineKeyboardButton(text="1 год за 1500 ⭐️ / 1999₽ / $19.99", callback_data="buy_stars_365")],
            [InlineKeyboardButton(text="💎 Стать VIP (2500 ⭐️)", callback_data="buy_stars_vip")]
        ]
    )

def gender_select_inline():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚹 Я Парень", callback_data="set_gender_M"),
                InlineKeyboardButton(text="🚺 Я Девушка", callback_data="set_gender_F")
            ]
        ]
    )

def target_gender_inline():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🚺 Искать только девушек (Премиум)", callback_data="target_F")],
            [InlineKeyboardButton(text="🚹 Искать только парней", callback_data="target_M")],
            [InlineKeyboardButton(text="🎲 Искать кого угодно (быстро)", callback_data="target_ANY")]
        ]
    )
