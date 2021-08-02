import requests
import lxml.html

from aiogram.dispatcher.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext

from loader import dp
from states.currency_converter_state import CurrencyConverterState
from keyboards.default import currencies_keyboards

currencies_dict = {
    'rub': "RUB",
    "usd": "USD",
    "euro": "EUR"
}


# Gets currency value
def parse_currency(dol_amount, cur_from, cur_to):
    url = f"https://www.xe.com/currencyconverter/convert/?Amount={dol_amount}&From={cur_from}&To={cur_to}"
    rub_xpath = "//main/form/div[2]/div[1]/p[2]/text()[1]"

    try:
        r = requests.get(url).text
        tree = lxml.html.document_fromstring(r)
        rub = tree.xpath(rub_xpath)[0]
    except:
        return None

    return rub


# Asks for currency to convert from
@dp.message_handler(Command("convert"))
async def convert_currency(message: Message):
    await message.answer(text="What currency do you want to convert from?",
                         reply_markup=currencies_keyboards.currencies_to_convert)
    await CurrencyConverterState.first()


# Asks for currency to convert to
@dp.message_handler(state=CurrencyConverterState.currency)
async def to_currencies(message: Message, state: FSMContext):
    if message.text in currencies_dict:
        await message.answer(text="What currency do you want to convert to?",
                             reply_markup=currencies_keyboards.currencies_to_convert)

        async with state.proxy() as data:
            data['currency_from'] = message.text
        await CurrencyConverterState.next()
    else:
        await message.answer(text="Guess you want me to convert it to Fluppy Coins or something?",
                             reply_markup=ReplyKeyboardRemove())
        await state.finish()


# Asks of value to convert
@dp.message_handler(state=CurrencyConverterState.currency_2)
async def currency_value(message: Message, state: FSMContext):
    if message.text in currencies_dict:
        await message.answer(text="How much, huh?",
                             reply_markup=ReplyKeyboardRemove())

        async with state.proxy() as data:
            data['currency_to'] = message.text
        await CurrencyConverterState.last()
    else:
        await message.answer(text="Is it funny? \n"
                                  "We'll see how much fun you'll get... when I <i><b>kill</b></i> you.\n"
                                  "Huh, just kidding.",
                             reply_markup=ReplyKeyboardRemove())
        await state.finish()


# Calculating and measuring bot answer
@dp.message_handler(state=CurrencyConverterState.currency_3)
async def answer_currency(message: Message, state: FSMContext):
    cur_value = message.text.strip()

    try:  # If data is float number
        float(cur_value)
        async with state.proxy() as data:

            cur_from = currencies_dict[data['currency_from']]  # Getting uppercase value
            cur_to = currencies_dict[data['currency_to']]  # Getting uppercase value

            # converted_cur = parse_currency(cur_value, cur_from, cur_to).split(".")[0]  # Getting converted value
            converted_cur = parse_currency(cur_value, cur_from, cur_to)  # Getting converted value
        if converted_cur is not None:  # It is None when bot can't connect to website where it parses data
            await message.answer(f"<b>{cur_value} {cur_from}</b> "
                                 f"is equal to <b>{converted_cur} {cur_to}</b>, bro!")
        else:
            await message.answer("Bro, I think something's wrong with my sources.\n"
                                 "Probably, they were <i><b>killed</b></i>.")
    except ValueError:
        await message.answer("Dude, you said you wanted to convert money, not a text!")

    await state.finish()
