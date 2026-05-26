import asyncio
from datetime import datetime

def is_poll_active() -> bool:
    return False
import logging
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


def candidates_page_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    per_page = 10
    start = page * per_page
    end = start + per_page
    page_candidates = CANDIDATES[start:end]
    total_pages = (len(CANDIDATES) + per_page - 1) // per_page

    buttons = []
    for c in page_candidates:
        buttons.append([
            InlineKeyboardButton(
                text=f"{c['name']} | {c['mahalla']}",
                callback_data=f"select_{c['id']}"
            )
        ])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"page_{page-1}"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=f"page_{page+1}"))
    if nav:
        buttons.append(nav)

    buttons.append([
        InlineKeyboardButton(text="📊 Natijalar", callback_data="results")
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
        InlineKeyboardButton(text="Nomzodlarga qaytish", callback_data="page_0")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def results_text() -> str:
    votes = db.get_all_votes()
    total = sum(votes.values()) or 1
    lines = ["Joriy natijalar:\n"]
    sorted_c = sorted(CANDIDATES, key=lambda c: votes.get(c["id"], 0), reverse=True)
    for i, c in enumerate(sorted_c[:10]):
        v = votes.get(c["id"], 0)
        pct = round(v / total * 100)
        bar = "=" * (pct // 5) + "-" * (20 - pct // 5)
        medal = ["1.", "2.", "3."][i] if i < 3 else f"{i+1}."
        lines.append(f"{medal} {c['name']}")
        lines.append(f"   {c['mahalla']}")
        lines.append(f"   [{bar}] {pct}% ({v} ovoz)\n")
    lines.append(f"Jami ishtirokchilar: {db.count_voters()} ta")
    return "\n".join(lines)


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    name = message.from_user.full_name

    args = message.text.split()
    if len(args) > 1 and args[1].startswith("vote_"):
        try:
            candidate_id = int(args[1].split("_")[1])
        except Exception:
            candidate_id = None

        if candidate_id:
            c = next((x for x in CANDIDATES if x["id"] == candidate_id), None)
            if c:
                if db.has_voted(user_id):
                    await message.answer("Siz allaqachon ovoz bergansiz!")
                    return
                not_joined = await check_subscriptions(user_id)
                if not not_joined:
                    db.save_vote(user_id, candidate_id)
                    await message.answer(
                        f"Ovozingiz qabul qilindi!\n\n"
                        f"Siz {c['name']} ga ovoz berdingiz\n"
                        f"{c['mahalla']}\n\n"
                        + results_text()
                    )
                else:
                    await message.answer(
                        f"Tanlovingiz: {c['name']}\n"
                        f"{c['mahalla']}\n\n"
                        f"Ovoz berish uchun avval quyidagi kanallarga obuna bo'ling:",
                        reply_markup=subscribe_keyboard(not_joined, candidate_id)
                    )
                return

    if db.has_voted(user_id):
        voted_id = db.get_user_vote(user_id)
        c = next((x for x in CANDIDATES if x["id"] == voted_id), None)
        await message.answer(
            f"{name}, siz allaqachon ovoz bergansiz!\n\n"
            f"Tanlovingiz: {c['name'] if c else '?'}\n"
            f"{c['mahalla'] if c else ''}\n\n"
            + results_text()
        )
        return

    await state.set_state(VoteState.choosing)
    await message.answer(
        f"Salom, {name}!\n\n"
        f"Shofirkon tumani eng faol maktab direktori so'rovnomasiga xush kelibsiz!\n\n"
        f"Quyidan ovoz bermoqchi bo'lgan nomzodni tanlang:",
        reply_markup=candidates_page_keyboard(0)
    )


@dp.callback_query(F.data.startswith("page_"))
async def page_callback(call: CallbackQuery, state: FSMContext):
    page = int(call.data.split("_")[1])
    await state.set_state(VoteState.choosing)
    try:
        await call.message.edit_text(
            "Ovoz bermoqchi bo'lgan nomzodni tanlang:",
            reply_markup=candidates_page_keyboard(page)
        )
    except TelegramBadRequest:
        pass
    await call.answer()


@dp.callback_query(F.data.startswith("select_"))
async def select_candidate(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

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
            f"Siz {c['name']} ga ovoz berdingiz\n"
            f"{c['mahalla']}\n\n"
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
            f"Tanlovingiz: {c['name']}\n"
            f"{c['mahalla']}\n\n"
            f"Ovoz berish uchun avval quyidagi kanallarga obuna bo'ling:",
            reply_markup=subscribe_keyboard(not_joined, candidate_id)
        )
        await call.answer()


@dp.callback_query(F.data.startswith("confirm_"))
async def confirm_vote(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    if db.has_voted(user_id):
        await call.answer("Siz allaqachon ovoz bergansiz!", show_alert=True)
        return

    candidate_id = int(call.data.split("_")[1])
    not_joined = await check_subscriptions(user_id)

    if not_joined:
        await call.answer("Hali barcha kanallarga obuna bo'lmadingiz!", show_alert=True)
        await call.message.edit_reply_markup(
            reply_markup=subscribe_keyboard(not_joined, candidate_id)
        )
        return

    c = next((x for x in CANDIDATES if x["id"] == candidate_id), None)
    db.save_vote(user_id, candidate_id)
    await state.clear()

    await call.message.edit_text(
        f"Ovozingiz qabul qilindi!\n\n"
        f"Siz {c['name']} ga ovoz berdingiz\n"
        f"{c['mahalla']}\n\n"
        + results_text(),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Natijalarni yangilash", callback_data="results")
        ]])
    )
    await call.answer("Ovoz saqlandi!")


@dp.callback_query(F.data == "results")
async def show_results(call: CallbackQuery):
    user_id = call.from_user.id
    if db.has_voted(user_id):
        markup = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Yangilash", callback_data="results")
        ]])
    else:
        markup = candidates_page_keyboard(0)
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
        "#Shofirkon_tumani\n\n"
        "Shofirkonda umumta'lim maktablari o'rtasida "
        "Eng faol va tashabbuskor maktab direktori onlayn tanlovi!\n\n"
        "Yoshlar ishlari Shofirkon tuman bo'limi hamda Shofirkon tuman "
        "maktabgacha va maktab ta'limi bo'limi tomonidan jamoatchilik "
        "so'rovnomasi o'tkazilmoqda.\n\n"
        "So'rovnoma orqali 2025-2026 o'quv yilidagi maktablar faoliyati, "
        "direktorlarning tashabbuskorligi va samaradorligi baholanadi.\n\n"
        "Sizningcha, Shofirkon tumanidagi qaysi maktab direktori "
        "eng faol va tashabbuskor?\n\n"
        "Eng yuqori natija qayd etgan maktab direktori tashakkurnoma "
        "va qimmatbaho sovg'alar bilan taqdirlanadi!\n\n"
        "So'rovnoma tugash muddati: 2026-yil 25-may soat 23:59"
    )

    buttons = []
    for c in CANDIDATES:
        buttons.append([
            InlineKeyboardButton(
                text=f"{c['name']} | {c['mahalla']}",
                url=f"https://t.me/shofirkon_sorovnoma_bot?start=vote_{c['id']}"
            )
        ])
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)

    await bot.send_photo(
        chat_id=channel,
        photo="https://raw.githubusercontent.com/asliddinmusic-sketch/voting-bot/main/banner%20(2).png",
        caption=caption,
        reply_markup=markup
    )
    await message.answer("Post kanalga yuborildi!")


async def main():
    print("Bot ishga tushdi!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
