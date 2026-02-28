import asyncio
import coc
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from set import BOT_TOKEN
from set import COC_TOKEN
from databs import Database
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State  

bot = Bot(token=BOT_TOKEN)
db = Database("----")
dp = Dispatcher()
coc_client = coc.Client()

class tag(StatesGroup):
    clan_tag = State()

@dp.message(Command("start"))
async def start_com(message: Message):
    await message.answer("старт бота")

@dp.message(Command("add"))
async def create_table_users(message: Message):
    button = InlineKeyboardButton(text="Кланы", callback_data="btn")
    board = InlineKeyboardMarkup(inline_keyboard=[[button]])
    await db.execute("""
        CREATE TABLE IF NOT EXISTS history_tags(
            tag TEXT,
            tgid BIGINT
        )
    """)
    await message.answer("Таблица создана", reply_markup=board)

@dp.callback_query(lambda x: x.data == "btn")
async def btn(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Напиши тег клана в формате #9L0JVJQU")
    await state.set_state(tag.clan_tag)
@dp.message(tag.clan_tag)
async def wait_tag(message: Message, state: FSMContext):
    clan_tag = message.text.strip()
    if not clan_tag.startswith("#"):
        await message.answer("введите тег клана, начинающийся с #.")
        return
    try:
        clan = await coc_client.get_clan(clan_tag)
        await message.answer(
    f"🔰|<b>Название клана:</b>  {clan.name}\n"
    f"🏆|<b>Трофеи:</b>  {clan.points}\n"
    f"👥|<b>Участников:</b>  {clan.member_count}\n\n"
    + "\n".join(
        f"{member.name} - {member.trophies} трофеев"
        for member in clan.members[:50]
    ), parse_mode="HTML"
)
        await db.execute("INSERT INTO history_tags (tag, tgid) VALUES ($1, $2)", clan_tag, message.from_user.id)
    except coc.errors.NotFound:
        await message.answer("Клан не найден. Пожалуйста, проверьте тег и попробуйте снова.")
    finally:
        await state.clear()

async def main():
    await db.connect()
    await coc_client.login_with_tokens(COC_TOKEN)
    await dp.start_polling(bot)
    await coc_client.close()
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
