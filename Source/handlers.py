from gc import callbacks

from aiogram import F, Router,types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.filters.callback_data import CallbackData


from motor.core import AgnosticDatabase as MDB
from contextlib import suppress
from pymongo.errors import DuplicateKeyError

from Source.keyboards import inline_builder
from Source.database import services_name, services_id, basket_append, basket, trash_can, set_user


router = Router()
@router.message(CommandStart())
async def start(message: Message | CallbackQuery, db: MDB):
    with suppress(DuplicateKeyError):
        await db.users.insert_one(await set_user(message.from_user.id))
    pattern =  dict(text ='Welcome to our Medical center',
                    reply_markup=inline_builder(
                        ['📝 Services', '🛒 Basket',' ✉️ Contact us',  '📑 About us'], ['services', 'basket', 'contact', 'about']))

    if isinstance(message, Message, CallbackQuery):
        await message.message.edit_text(**pattern)
    else:
        await message.answer(**pattern)


@router.callback_query(F.data == 'main_menu')
async def main_menu(callback: CallbackQuery, db: MDB):
    await callback.answer()
    await  callback.message.edit_text(
        text='Main page',
        reply_markup=inline_builder(['📝 Services', '🛒 Basket',' ✉️ Contact us',  '📑 About us'], ['services', 'basket', 'contact', 'about'])
    )


@router.callback_query(F.data == 'services')
@router.callback_query(F.data == 'to_services')
async def show_services(callback: CallbackQuery, db: MDB):
    text = await services_name()
    cb = await services_id()
    text.append('⬅️Back to main menu')
    cb.append('main_page')
    await callback.answer()
    await callback.message.edit_text(text='Choose a service',
                                     reply_markup=inline_builder(text, cb))
@router.callback_query(F.date.startswith('callback'))
async def show_doctors(callback: CallbackQuery, db: MDB):
    id = callback.data.split('_')[1]
    await callback.answer()
    await callback.message.edit_text(text=f'Choose a doctor',
                                     reply_markup=inline_builder(['⬅️Back to main menu'], ['main_page']))