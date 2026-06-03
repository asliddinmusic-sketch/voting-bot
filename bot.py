import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.exceptions import TelegramBadRequest

from config import BOT_TOKEN, CHANNELS, CANDIDATES, ADMIN_IDS
from database import db

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


def is_poll_active() -> bool:
    now = datetime.now()
    end = datetime(2026, 6, 6, 23, 59, 59)
    return now < end


class VoteState(StatesGroup):
    choosing = State()
    subscribing = State()


async def check_subscriptions(user_id: int) -> list:
    not_joined = []
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(ch["id"], user_id)
            if member.status in ("left", "kicked", "banned"):
                not_joined.append(ch)
        except TelegramBadRequest:
            not_joined.append(ch)
    return not_joined


def candidates_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for c in CANDIDATES:
        buttons.append([
            InlineKeyboardButton(
                text=f"{c['name']}",
                callback_data=f"select_{c['id']}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(text="Natijalar", callback_data="results")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def subscribe_keyboard(not_joined: list, candidate_id: int) -> InlineKeyboardMarkup:
    buttons = []
    for ch in not_joined:
        buttons.append([
            InlineKeyboardButton(text=ch['name'], url=ch["invite_link"])
        ])
    buttons.append([
        InlineKeyboardButton(
            text="Obuna bo'ldim, tekshiring!",
            callback_data=f"confirm_{candidate_id}"
        )
    ])
    buttons.append([
        InlineKeyboardButton(text="Ortga", callback_data="back")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def results_text() -> str:
    votes = db.get_all_votes()
    total = sum(votes.values()) or 1
    lines = ["Joriy natijalar:\n"]
    sorted_c = sorted(CANDIDATES, key=lambda c: votes.get(c["id"], 0), reverse=True)
    for i, c in enumerate(sorted_c):
        v = votes.get(c["id"], 0)
        pct = round(v / total * 100)
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        medal = ["1.", "2.", "3.", "4."][i] if i < 4 else f"{i+1}."
        lines.append(f"{medal} {c['name']}")
        lines.append(f"   {bar} {pct}% ({v} ovoz)\n")
    lines.append(f"Jami ishtirokchilar: {db.count_voters()} ta")
    return "\n".join(lines)


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    name = message.from_user.full_name

    args = message.text.split()
    if len(args) > 1 and args[1].startswith("vote_"):
        if not is_poll_active():
            await message.answer("So'rovnoma 06.06.2026 da yakunlandi!\n\n" + results_text())
            return
        try:
            candidate_id = int(args[1].split("_")[1])
        except Exception:
            candidate_id = None

        if candidate_id:
            c = next((x for x in CANDIDATES if x["id"] == candidate_id), None)
            if c:
                if db.has_voted(user_id):
                    await message.answer("Siz allaqachon ovoz bergansiz!\n\n" + results_text())
                    return
                not_joined = await check_subscriptions(user_id)
                if not not_joined:
                    db.save_vote(user_id, candidate_id)
                    await message.answer(
                        f"Ovozingiz qabul qilindi!\n\n"
                        f"Siz {c['name']} ga ovoz berdingiz\n\n"
                        + results_text()
                    )
                else:
                    await message.answer(
                        f"Tanlovingiz: {c['name']}\n\n"
                        f"Ovoz berish uchun avval quyidagi kanalga obuna bo'ling:",
                        reply_markup=subscribe_keyboard(not_joined, candidate_id)
                    )
                return

    if db.has_voted(user_id):
        voted_id = db.get_user_vote(user_id)
        c = next((x for x in CANDIDATES if x["id"] == voted_id), None)
        await message.answer(
            f"{name}, siz allaqachon ovoz bergansiz!\n\n"
            f"Tanlovingiz: {c['name'] if c else '?'}\n\n"
            + results_text()
        )
        return

    if not is_poll_active():
        await message.answer("So'rovnoma 06.06.2026 da yakunlandi!\n\n" + results_text())
        return

    await state.set_state(VoteState.choosing)
    await message.answer(
        f"Salom, {name}!\n\n"
        f"Yoshlar kunida qaysi san'atkorni Shofirkonga taklif qilishimizni xohlaysiz?\n\n"
        f"Quyidan o'z nomzodingizni tanlang:",
        reply_markup=candidates_keyboard()
    )


@dp.callback_query(F.data == "back")
async def back_callback(call: CallbackQuery, state: FSMContext):
    await state.set_state(VoteState.choosing)
    try:
        await call.message.edit_text(
            "Quyidan o'z nomzodingizni tanlang:",
            reply_markup=candidates_keyboard()
        )
    except TelegramBadRequest:
        pass
    await call.answer()


@dp.callback_query(F.data.startswith("select_"))
async def select_candidate(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    if not is_poll_active():
        await call.answer("So'rovnoma tugadi!", show_alert=True)
        return

    if db.has_voted(user_id):
        await call.answer("Siz allaqachon ovoz bergansiz!", show_alert=True)
        return

    candidate_id = int(call.data.split("_")[1])
    c = next((x for x in CANDIDATES if x["id"] == candidate_id), None)
    if not c:
        await call.answer("Xatolik!", show_alert=True)
        return

    not_joined = await check_subscriptions(user_id)

    if not not_joined:
        db.save_vote(user_id, candidate_id)
        await call.message.edit_text(
            f"Ovozingiz qabul qilindi!\n\n"
            f"Siz {c['name']} ga ovoz berdingiz\n\n"
            + results_text(),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text="Natijalarni yangilash", callback_data="results")
            ]])
        )
        await call.answer("Ovoz saqlandi!")
    else:
        await state.set_state(VoteState.subscribing)
        await state.update_data(pending_candidate=candidate_id)
        await call.message.edit_text(
            f"Tanlovingiz: {c['name']}\n\n"
            f"Ovoz berish uchun avval quyidagi kanalga obuna bo'ling:",
            reply_markup=subscribe_keyboard(not_joined, candidate_id)
        )
        await call.answer()


@dp.callback_query(F.data.startswith("confirm_"))
async def confirm_vote(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    if not is_poll_active():
        await call.answer("So'rovnoma tugadi!", show_alert=True)
        return

    if db.has_voted(user_id):
        await call.answer("Siz allaqachon ovoz bergansiz!", show_alert=True)
        return

    candidate_id = int(call.data.split("_")[1])
    not_joined = await check_subscriptions(user_id)

    if not_joined:
        await call.answer("Hali kanalga obuna bo'lmadingiz!", show_alert=True)
        await call.message.edit_reply_markup(
            reply_markup=subscribe_keyboard(not_joined, candidate_id)
        )
        return

    c = next((x for x in CANDIDATES if x["id"] == candidate_id), None)
    db.save_vote(user_id, candidate_id)
    await state.clear()

    await call.message.edit_text(
        f"Ovozingiz qabul qilindi!\n\n"
        f"Siz {c['name']} ga ovoz berdingiz\n\n"
        + results_text(),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Natijalarni yangilash", callback_data="results")
        ]])
    )
    await call.answer("Ovoz saqlandi!")


@dp.callback_query(F.data == "results")
async def show_results(call: CallbackQuery):
    user_id = call.from_user.id

    not_joined = await check_subscriptions(user_id)
    if not_joined:
        await call.answer("Natijalarni ko'rish uchun kanalga obuna bo'ling!", show_alert=True)
        await call.message.edit_text(
            "Natijalarni ko'rish uchun avval kanalga obuna bo'ling:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                *[[InlineKeyboardButton(text=ch['name'], url=ch["invite_link"])] for ch in not_joined],
                [InlineKeyboardButton(text="Tekshirish", callback_data="results")]
            ])
        )
        return

    if db.has_voted(user_id):
        markup = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Yangilash", callback_data="results")
        ]])
    else:
        markup = candidates_keyboard()
    try:
        await call.message.edit_text(results_text(), reply_markup=markup)
    except TelegramBadRequest:
        pass
    await call.answer()


@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer(results_text())


@dp.message(Command("reset"))
async def cmd_reset(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    db.reset_votes()
    await message.answer("Barcha ovozlar o'chirildi.")


@dp.message(Command("sendpoll"))
async def cmd_sendpoll(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    channel = "@YIA_Shofirkon_tumani"

    caption = (
        "Yoshlar kuni munosabati bilan!\n\n"
        "Qaysi san'atkorni Shofirkonda ko'rishni xohlaysiz?\n\n"
        "Sizning fikringiz biz uchun muhim! Yoshlar kuniga bag'ishlangan "
        "bayram dasturida qaysi san'atkor ishtirok etishini birgalikda tanlaymiz.\n\n"
        "Ovoz bering va o'z tanlovingizni belgilang!\n\n"
        "Rasmdagi san'atkorlardan biriga ovoz bering\n\n"
        "Eng faol va eng ko'p ovoz to'plagan nomzodlar ko'rib chiqiladi.\n\n"
        "Do'stlaringizga ham ulashing va ovoz berishda ishtirok eting!\n\n"
        "So'rovnoma tugash muddati: 2026-yil 6-iyun soat 23:59"
    )

    buttons = []
    for c in CANDIDATES:
        buttons.append([
            InlineKeyboardButton(
                text=f"{c['name']}",
                url=f"https://t.me/shofirkon_sorovnoma_bot?start=vote_{c['id']}"
            )
        ])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await bot.send_photo(
        chat_id=channel,
        photo="https://raw.githubusercontent.com/asliddinmusic-sketch/voting-bot/main/yoshlar_kuni.jpg",
        caption=caption,
        reply_markup=markup
    )
    await message.answer("Post kanalga yuborildi!")


async def main():
    print("Bot ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
