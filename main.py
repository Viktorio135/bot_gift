import config

from aiogram import Bot, Dispatcher, types, filters
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor

import models



bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

user_history = dict()


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):

    user_history[message.from_user.id] = []

    inline_btn1 = types.InlineKeyboardButton(
            text='Catalog',
            callback_data='catalog_menu'
        )
    keyboard = types.InlineKeyboardMarkup().add(inline_btn1)

    await bot.send_photo(
            message.from_user.id,
            open('static/start.png', 'rb'),
            'Привет, ты попал в лучший магазин по продаже подарочных сертификатов для различных сервисов!'
        )

    await bot.send_message(
            message.from_user.id, 
            'Select', 
            reply_markup=keyboard
        )




@dp.callback_query_handler(lambda c: 'catalog_menu' in c.data)
async def cmd_catalog(callback_query: types.CallbackQuery):

    if ':cancel' in callback_query.data:
        user_history[callback_query.from_user.id].pop()
    else:
        user_history[callback_query.from_user.id].append('catalog_menu')

    categories_list = models.read_category()

    inline_keyboard = types.InlineKeyboardMarkup()
    for category in categories_list:
        inline_keyboard.add(
            types.InlineKeyboardButton(
                text=category, 
                callback_data=f'category_menu:{category}'
                )
            )

    if len(user_history[callback_query.from_user.id])>2:
        inline_keyboard.add(types.InlineKeyboardButton(
                text='Назад', 
                callback_data=f'{user_history[callback_query.from_user.id][-2]}:cancel'
                )
            )

    await callback_query.message.delete()
    await bot.send_message(
            callback_query.from_user.id, 
            'Select', 
            reply_markup=inline_keyboard
        )



@dp.callback_query_handler(lambda c: 'category_menu' in c.data)
async def cmd_spotify(callback_query: types.CallbackQuery):

    if ':cancel' in callback_query.data:
        user_history[callback_query.from_user.id].pop()
    else:
        user_history[callback_query.from_user.id].append(callback_query.data)

    category_munu = callback_query.data.split(':')[1]
    await bot.answer_callback_query(callback_query.id)
    inline_keyboard = types.InlineKeyboardMarkup()
    goods = models.read_rate(category_name=category_munu)

    for good in goods:
        inline_keyboard.add(types.InlineKeyboardButton(
                    text=good.rate, 
                    callback_data=f'rate_menu:{good.name_category}:{good.rate}'
                )
            )
    
    if len(user_history[callback_query.from_user.id])>=2:
        inline_keyboard.add(types.InlineKeyboardButton(
                    text='Назад', 
                    callback_data=f'{user_history[callback_query.from_user.id][-2]}:cancel'
                )
            )

    await callback_query.message.delete()
    await bot.send_message(
            callback_query.from_user.id, 
            'Select', 
            reply_markup=inline_keyboard
        )


@dp.callback_query_handler(lambda c: 'rate_menu' in c.data)
async def cmd_rate(callback_query: types.CallbackQuery):

    if ':cancel' in callback_query.data:
        user_history[callback_query.from_user.id].pop()
    else:
        user_history[callback_query.from_user.id].append(callback_query.data)

    request = callback_query.data.split(':')
    category = request[1]
    rate = request[2]

    await bot.answer_callback_query(callback_query.id)
    await callback_query.message.delete()

    inline_btn1 = types.InlineKeyboardButton(
            text='Купить', 
            callback_data=f'buy:{category}:{rate}'
        )
    inline_keyboard = types.InlineKeyboardMarkup().add(inline_btn1)

    if len(user_history[callback_query.from_user.id])>2:
        inline_btn2 = types.InlineKeyboardButton(
                text='Назад', 
                callback_data=f'{user_history[callback_query.from_user.id][-2]}:cancel'
            )
        inline_keyboard.add(inline_btn2)
    
    await bot.send_message(
            callback_query.from_user.id, 
            f'{request}\n{category}\n{rate}', 
            reply_markup=inline_keyboard
        )


@dp.callback_query_handler(lambda c: 'buy:' in c.data)
async def cmd_buy(callback_query: types.CallbackQuery):

    await bot.answer_callback_query(callback_query.id)

    if ':cancel' in callback_query.data:
        user_history[callback_query.from_user.id].pop()
    else:
        user_history[callback_query.from_user.id].append(callback_query.data)

    request = callback_query.data.split(':')
    category = request[1]
    rate = request[2]

    inline_btn1 = types.InlineKeyboardButton(
            text='Назад', 
            callback_data=f'{user_history[callback_query.from_user.id][-2]}:cancel'
        )
    inline_keyboard = types.InlineKeyboardMarkup().add(inline_btn1)

    await callback_query.message.delete()
    await bot.send_message(
            callback_query.from_user.id, 
            'Успешно', 
            reply_markup=inline_keyboard
        )






class Form_category_append(StatesGroup):
    category_name = State()

class Form_category_remove(StatesGroup):
    category_name = State()

class Form_goods_append(StatesGroup):
    category_name = State()
    good_name = State()

class Form_goods_remove(StatesGroup):
    category_name = State()
    good_name = State()


@dp.message_handler(commands=['admin'])
async def cmd_admin(message: types.Message):

    inline_btn1 = types.InlineKeyboardButton(text='Категории', callback_data='category')
    inline_btn2 = types.InlineKeyboardButton(text='Товары', callback_data='goods')

    keyboard = types.InlineKeyboardMarkup().add(inline_btn1, inline_btn2)

    await bot.send_message(message.from_user.id, 'select', reply_markup=keyboard)


@dp.callback_query_handler(lambda c: c.data == 'goods')
async def adminGoods(callback_query: types.CallbackQuery):
        
    await callback_query.message.delete()

    inline_btn1 = types.InlineKeyboardButton(text='Добавить', callback_data='append_goods')
    inline_btn2 = types.InlineKeyboardButton(text='Удалить', callback_data='remove_goods')

    inline_keyboard = types.InlineKeyboardMarkup().add(inline_btn1, inline_btn2)

    await bot.send_message(callback_query.from_user.id, 'Select', reply_markup=inline_keyboard)

@dp.callback_query_handler(lambda c: c.data == 'remove_goods')
async def adminGoods(callback_query: types.CallbackQuery):
        
    await callback_query.message.delete()

    await Form_goods_remove.category_name.set()

    categories_list = models.read_category()

    text_string = ''

    for category in categories_list:
        text_string += f'{category}\n'
    
    await bot.send_message(callback_query.from_user.id, f'Введите название категории, тариф которой вы хотите удалить.\nСписок доступных категорий:\n{text_string}')

@dp.message_handler(state=Form_goods_remove.category_name)
async def stateGoodsName(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['category_name'] = message.text

    await Form_goods_remove.next()

    rates_list = models.read_rate(category_name=data['category_name'])

    text_string = ''

    for rate_obj in rates_list:
        text_string += f'{rate_obj.rate}\n'
    

    await bot.send_message(message.from_user.id, f'Введите название тарифа\nДоступные тарифы:\n{text_string}')

@dp.message_handler(state=Form_goods_remove.good_name)
async def stateGoodsName(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['good_name'] = message.text

    await state.finish()

    models.remove_rate(data['good_name'], data['category_name'])

    inline_btn = types.InlineKeyboardButton(text='Вернуться обратно', callback_data='catalog_menu')
    keyboard = types.InlineKeyboardMarkup.add(inline_btn)

    await bot.send_message(message.from_user.id, 'Тариф успешно удален', reply_markup=keyboard)



@dp.callback_query_handler(lambda c: c.data == 'append_goods')
async def adminCategory(callback_query: types.CallbackQuery):
        
    await callback_query.message.delete()

    await Form_goods_append.category_name.set()

    categories_list = models.read_category()

    text_string = ''

    for category in categories_list:
        text_string += f'{category}\n'
    
    await bot.send_message(callback_query.from_user.id, f'Введите название категории, которой хотите добавить тариф.\nСписок доступных категорий:\n{text_string}')


@dp.message_handler(state=Form_goods_append.category_name)
async def stateGoodsName(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['category_name'] = message.text

    await Form_goods_append.next()

    await bot.send_message(message.from_user.id, 'Введите название тарифа')
    
@dp.message_handler(state=Form_goods_append.good_name)
async def stateGoodsName(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['goods_name'] = message.text

    await state.finish()

    models.create_rate(data['goods_name'], data['category_name'])

    inline_btn = types.InlineKeyboardButton(text='Вернуться обратно', callback_data='catalog_menu')
    keyboard = types.InlineKeyboardMarkup().add(inline_btn)


    await bot.send_message(message.from_user.id, 'Товар успешно добавлен', reply_markup=keyboard)



@dp.callback_query_handler(lambda c: c.data == 'category')
async def adminCategory(callback_query: types.CallbackQuery):
        

    await callback_query.message.delete()

    inline_btn1 = types.InlineKeyboardButton(text='Добавить', callback_data='append_category')
    inline_btn2 = types.InlineKeyboardButton(text='Удалить', callback_data='remove_category')

    inline_keyboard = types.InlineKeyboardMarkup().add(inline_btn1, inline_btn2)

    await bot.send_message(callback_query.from_user.id, 'Select', reply_markup=inline_keyboard)

@dp.callback_query_handler(lambda c: c.data == 'append_category')
async def appendCategory(callback_query: types.CallbackQuery):

    await bot.answer_callback_query(callback_query.id)

    await Form_category_append.category_name.set()

    await callback_query.message.delete()

    await bot.send_message(callback_query.from_user.id, 'Введите название категории')

        
@dp.message_handler(state=Form_category_append.category_name)
async def stateCategoryName(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['category_name'] = message.text
    
    await state.finish()

    models.create_category(data['category_name'])
    inline_btn = types.InlineKeyboardButton(text='Вернуться обратно', callback_data='catalog_menu')
    keyboard = types.InlineKeyboardMarkup().add(inline_btn)

    await bot.send_message(message.from_user.id, 'Категория доблена', reply_markup=keyboard)



@dp.callback_query_handler(lambda c: c.data == 'remove_category')
async def removeCategory(callback_query: types.CallbackQuery):

    await bot.answer_callback_query(callback_query.id)

    categories_list = models.read_category()

    text_string = 'На данные момент доступны данные категории:\n'

    for category in categories_list:
        text_string += f'{category}\n'
    text_string += 'напишите название категории для ее удаления'

    await Form_category_remove.category_name.set()

    await bot.send_message(callback_query.from_user.id, text_string)


@dp.message_handler(state=Form_category_remove.category_name)
async def stateCategoryName(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['category_name'] = message.text
    
    await state.finish()

    models.remove_category(data['category_name'])

    inline_btn = types.InlineKeyboardButton(text='Вернуться обратно', callback_data='catalog_menu')
    keyboard = types.InlineKeyboardMarkup().add(inline_btn)

    await bot.send_message(message.from_user.id, 'Категория успешно удалена', reply_markup=keyboard)





if __name__ == '__main__':
    models.start_database()
    executor.start_polling(dp, skip_updates=True)





