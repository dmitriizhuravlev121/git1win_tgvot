from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext, CallbackQueryHandler
import pandas as pd
import os
my_secret = os.environ['API_TG']

# Шаги для диалога
TASK_NAME, TASK_ACTION, QUANTITY, COLOR, MATERIAL, DENSITY, FURNITURE, SEAMS, APPLY, PATTERNS, GRADATION, LINK, DEADLINE, COST, APPROVAL, CUSTOM_GRADATION = range(16)

# Пустой DataFrame для хранения ответов
answers_df = pd.DataFrame(columns=[
    "Username", "Task Name", "Task Action", "Quantity", "Color", "Material", "Density",
    "Furniture", "Seams", "Apply", "Patterns", "Gradation", "Link", "Deadline", "Cost", "Approval"
])

# Стартовая команда
async def start(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("Привет! Введи название задачи:")
    return TASK_NAME

# Вопрос о названии задачи
async def task_name(update: Update, context: CallbackContext) -> int:
    context.user_data['task_name'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("Пошив", callback_data='Пошив')],
        [InlineKeyboardButton("Снятие лекал", callback_data='Снятие лекал')],
        [InlineKeyboardButton("Нанесение", callback_data='Нанесение')],
        [InlineKeyboardButton("Вышивка", callback_data='Вышивка')],
        [InlineKeyboardButton("Переделать", callback_data='Переделать')],
        [InlineKeyboardButton("Комплекс", callback_data='Комплекс')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Что нужно сделать? (Выберите вариант):", reply_markup=reply_markup)
    return TASK_ACTION

# Обработчик выбора действия
async def handle_task_action(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()
    context.user_data['task_action'] = query.data
    await query.edit_message_text(f"Вы выбрали: {query.data}")
    await query.message.reply_text("В каком количестве?")
    return QUANTITY

# Вопрос о количестве
async def quantity(update: Update, context: CallbackContext) -> int:
    context.user_data['quantity'] = update.message.text
    await update.message.reply_text("Какого цвета?")
    return COLOR

# Вопрос о цвете
async def color(update: Update, context: CallbackContext) -> int:
    context.user_data['color'] = update.message.text
    await update.message.reply_text("Из какого материала?")
    return MATERIAL

# Вопрос о материале
async def material(update: Update, context: CallbackContext) -> int:
    context.user_data['material'] = update.message.text
    await update.message.reply_text("Какая плотность?")
    return DENSITY

# Вопрос о плотности
async def density(update: Update, context: CallbackContext) -> int:
    context.user_data['density'] = update.message.text
    await update.message.reply_text("ТЗ по фурнитуре:")
    return FURNITURE

# Вопрос о фурнитуре
async def furniture(update: Update, context: CallbackContext) -> int:
    context.user_data['furniture'] = update.message.text
    await update.message.reply_text("ТЗ по швам:")
    return SEAMS

# Вопрос о швах
async def seams(update: Update, context: CallbackContext) -> int:
    context.user_data['seams'] = update.message.text
    await update.message.reply_text("ТЗ по нанесению (какое и размер):")
    return APPLY

# Вопрос о нанесении
async def apply(update: Update, context: CallbackContext) -> int:
    context.user_data['apply'] = update.message.text
    await update.message.reply_text("Какие лекала (если они сняты) и есть ли по ним правки?")
    return PATTERNS

# Вопрос о лекалах
async def patterns(update: Update, context: CallbackContext) -> int:
    context.user_data['patterns'] = update.message.text

    keyboard = [
        [InlineKeyboardButton("XS", callback_data='XS')],
        [InlineKeyboardButton("S", callback_data='S')],
        [InlineKeyboardButton("M", callback_data='M')],
        [InlineKeyboardButton("L", callback_data='L')],
        [InlineKeyboardButton("XL", callback_data='XL')],
        [InlineKeyboardButton("XXL", callback_data='XXL')],
        [InlineKeyboardButton("Свой вариант", callback_data='custom')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Нужна ли градация лекал и какие размеры?", reply_markup=reply_markup)
    return GRADATION

# Обработчик выбора в градации лекал
async def handle_gradation_choice(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    if query.data == 'custom':
        await query.edit_message_text("Введите свой вариант размеров:")
        return CUSTOM_GRADATION  # Переход в состояние, где пользователь введет свой ответ
    else:
        context.user_data['gradation'] = query.data
        await query.edit_message_text(f"Вы выбрали: {query.data}")
        await query.message.reply_text("Ссылка на макет:")
        return LINK

# Обработчик для пользовательского варианта градации лекал
async def custom_gradation(update: Update, context: CallbackContext) -> int:
    context.user_data['gradation'] = update.message.text
    await update.message.reply_text(f"Вы ввели свой вариант размеров: {context.user_data['gradation']}")
    await update.message.reply_text("Ссылка на макет:")
    return LINK

# Вопрос о ссылке на макет
async def link(update: Update, context: CallbackContext) -> int:
    context.user_data['link'] = update.message.text
    await update.message.reply_text("Дедлайн без учета доставки:")
    return DEADLINE

# Вопрос о дедлайне
async def deadline(update: Update, context: CallbackContext) -> int:
    context.user_data['deadline'] = update.message.text
    await update.message.reply_text("Кост для оплаты:")
    return COST

# Вопрос о стоимости
async def cost(update: Update, context: CallbackContext) -> int:
    context.user_data['cost'] = update.message.text
    await update.message.reply_text("Апрув от заказчика по смете:")
    return APPROVAL

# Вопрос об апруве
async def approval(update: Update, context: CallbackContext) -> int:
    context.user_data['approval'] = update.message.text

    # Сохраняем ответы в таблицу
    global answers_df
    new_row = pd.DataFrame([{
        "Username": update.message.from_user.username,
        "Task Name": context.user_data['task_name'],
        "Task Action": context.user_data['task_action'],
        "Quantity": context.user_data['quantity'],
        "Color": context.user_data['color'],
        "Material": context.user_data['material'],
        "Density": context.user_data['density'],
        "Furniture": context.user_data['furniture'],
        "Seams": context.user_data['seams'],
        "Apply": context.user_data['apply'],
        "Patterns": context.user_data['patterns'],
        "Gradation": context.user_data['gradation'],
        "Link": context.user_data['link'],
        "Deadline": context.user_data['deadline'],
        "Cost": context.user_data['cost'],
        "Approval": context.user_data['approval']
    }])
    answers_df = pd.concat([answers_df, new_row], ignore_index=True)

    # Форматируем таблицу как строку
    table_str = (
        f"Название задачи. Для кого и что?: {context.user_data['task_name']}\n"
        f"Что нужно сделать?: {context.user_data['task_action']}\n"
        f"Тираж: {context.user_data['quantity']}\n"
        f"Цвет: {context.user_data['color']}\n"
        f"Материал: {context.user_data['material']}\n"
        f"Плотность: {context.user_data['density']}\n"
        f"ТЗ по фурнитуре: {context.user_data['furniture']}\n"
        f"ТЗ по швам: {context.user_data['seams']}\n"
        f"ТЗ по нанесению (какое и размер): {context.user_data['apply']}\n"
        f"Какие лекала (если они сняты) и есть ли по ним правки: {context.user_data['patterns']}\n"
        f"Нужна ли градация лекал и какие размеры?: {context.user_data['gradation']}\n"
        f"Ссылка на макет, выполненный в соответствии с ТТ производства: {context.user_data['link']}\n"
        f"Дедлайн без учета доставки (сроки по доставке от заказчика или хостинга): {context.user_data['deadline']}\n"
        f"Кост для оплаты: {context.user_data['cost']}\n"
        f"Апрув от заказчика по смете: {context.user_data['approval']}\n"
    )

    await update.message.reply_text("Вот ваша таблица:")
    await update.message.reply_text(table_str)

    return ConversationHandler.END

# Обработчик ошибок
async def error(update: Update, context: CallbackContext) -> None:
    print(f"Update {update} caused error {context.error}")

# Создание приложения и добавление обработчиков
def main() -> None:
    application = Application.builder().token("7320988841:AAFNPsDo_srho3IBABaoCw2lLt2-JmLtQGY").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, task_name)],
            TASK_ACTION: [CallbackQueryHandler(handle_task_action)],
            QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, quantity)],
            COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, color)],
            MATERIAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, material)],
            DENSITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, density)],
            FURNITURE: [MessageHandler(filters.TEXT & ~filters.COMMAND, furniture)],
            SEAMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, seams)],
            APPLY: [MessageHandler(filters.TEXT & ~filters.COMMAND, apply)],
            PATTERNS: [MessageHandler(filters.TEXT & ~filters.COMMAND, patterns)],
            GRADATION: [CallbackQueryHandler(handle_gradation_choice)],
            CUSTOM_GRADATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, custom_gradation)],
            LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, link)],
            DEADLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, deadline)],
            COST: [MessageHandler(filters.TEXT & ~filters.COMMAND, cost)],
            APPROVAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, approval)],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, error))

    application.run_polling()

if __name__ == '__main__':
    main()
