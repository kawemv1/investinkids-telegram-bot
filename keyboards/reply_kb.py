from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню для пользователя"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🔧 Сообщить о проблеме")
    )
    builder.row(
        KeyboardButton(text="💡 Оставить предложение"),
        KeyboardButton(text="💬 Обратная связь")
    )
    builder.row(
        KeyboardButton(text="📋 Мои обращения")
    )
    return builder.as_markup(resize_keyboard=True)

def get_request_type_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура выбора типа проблемы"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🏫 Помещение/оборудование")
    )
    builder.row(
        KeyboardButton(text="📚 Учебный процесс")
    )
    builder.row(
        KeyboardButton(text="👥 Персонал")
    )
    builder.row(
        KeyboardButton(text="🔙 Назад")
    )
    return builder.as_markup(resize_keyboard=True)

def get_photo_choice_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура выбора - с фото или без"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📷 Добавить фото"),
        KeyboardButton(text="➡️ Продолжить без фото")
    )
    builder.row(
        KeyboardButton(text="🔙 Назад")
    )
    return builder.as_markup(resize_keyboard=True)

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="❌ Отменить")
    )
    return builder.as_markup(resize_keyboard=True)

def get_admin_action_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для админа"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="✅ Взять в работу")
    )
    return builder.as_markup(resize_keyboard=True)

