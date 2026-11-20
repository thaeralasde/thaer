import asyncio
import os
import re
import uuid
from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

# يقرأ التوكن بأمان من Environment Variables في Render
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# رقم User ID الخاص بحسابك كمالك للبوت
OWNER_ID = 5604018753

if not BOT_TOKEN:
    raise RuntimeError("يرجى ضبط متغير البيئة BOT_TOKEN قبل تشغيل البوت.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

whispers: dict[str, dict] = {}


@dp.inline_query()
async def handle_inline_query(inline_query: InlineQuery) -> None:
    query = inline_query.query.strip()
    match = re.match(r"^@([A-Za-z0-9_]{3,32})\s+(.+)$", query, flags=re.DOTALL)

    if not match:
        help_result = InlineQueryResultArticle(
            id="help_whisper",
            title="طريقة إرسال همسة",
            description="اكتب: @username نص الهمسة",
            input_message_content=InputTextMessageContent(
                message_text="لإرسال همسة اكتب:\n@Hamssa22114_bot @username نص الهمسة"
            ),
        )
        await inline_query.answer([help_result], cache_time=1, is_personal=True)
        return

    target_username = match.group(1).lower()
    whisper_text = match.group(2).strip()
    whisper_id = uuid.uuid4().hex[:10]

    whispers[whisper_id] = {
        "target_username": target_username,
        "text": whisper_text,
        "sender_id": inline_query.from_user.id,
    }

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="فتح الهمسة 🔒",
                    callback_data=f"open_whisper:{whisper_id}",
                )
            ]
        ]
    )

    result = InlineQueryResultArticle(
        id=whisper_id,
        title=f"إرسال همسة إلى @{match.group(1)}",
        description="اضغط لإرسال الهمسة في المحادثة",
        input_message_content=InputTextMessageContent(
            message_text=f"همسة سرية موجّهة إلى @{match.group(1)} 🤫"
        ),
        reply_markup=keyboard,
    )

    await inline_query.answer([result], cache_time=1, is_personal=True)


@dp.callback_query(F.data.startswith("open_whisper:"))
async def handle_open_whisper(callback: CallbackQuery) -> None:
    whisper_id = callback.data.split(":", 1)[1]
    data = whispers.get(whisper_id)

    if not data:
        await callback.answer("انتهت صلاحية هذه الهمسة أو تم إعادة تشغيل البوت.", show_alert=True)
        return

    clicker_id = callback.from_user.id
    clicker_username = (callback.from_user.username or "").lower()

    is_owner = clicker_id == OWNER_ID
    is_target = bool(clicker_username) and clicker_username == data["target_username"]

    if is_owner or is_target:
        await callback.answer(text=data["text"], show_alert=True)
    else:
        await callback.answer("هذه الهمسة ليست لك! ❌", show_alert=True)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
