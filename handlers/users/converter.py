import requests
import lxml.html

from aiogram.dispatcher.filters import Command
from aiogram.types import Message
from aiogram.dispatcher import FSMContext

from loader import dp
from states.currency_converter_state import CurrencyConverterState


def parse_currency(dol_amount):
    url = f"https://www.xe.com/currencyconverter/convert/?Amount={dol_amount}&From=USD&To=RUB"
    rub_xpath = "//main/form/div[2]/div[1]/p[2]/text()[1]"

    try:
        r = requests.get(url).text
        tree = lxml.html.document_fromstring(r)
        rub = tree.xpath(rub_xpath)[0]
    except:
        return None

    return rub


@dp.message_handler(Command("convert"), state=None)
async def convert_currency(message: Message):
    await message.answer("Tell me in usd what to convert to rub.")

    await CurrencyConverterState.first()


@dp.message_handler(state=CurrencyConverterState.currency)
async def answer_currency(message: Message, state: FSMContext):
    cur = message.text.strip()

    try:
        float(cur)
        converted_cur = parse_currency(cur).split(".")[0]
        if converted_cur is not None:
            await message.answer(f"<b>{cur} usd</b> is equal to <b>{converted_cur} rub</b>, bro!")
        else:
            await message.answer("Bro, I think something's wrong with my sources.\n"
                                 "Probably, they were <i><b>killed</b></i>.")
    except ValueError:
        await message.answer("Dude, you said you wanted to convert money, not a text!")

    await state.finish()
