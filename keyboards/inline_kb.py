from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu() -> InlineKeyboardMarkup:
    """Главное меню для пользователя"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔧 Сообщить о проблеме", callback_data="report_problem")
    )
    builder.row(
        InlineKeyboardButton(text="💡 Оставить предложение", callback_data="suggestion")
    )
    builder.row(
        InlineKeyboardButton(text="💬 Обратная связь", callback_data="feedback")
    )
    builder.row(
        InlineKeyboardButton(text="📋 Мои обращения", callback_data="my_requests")
    )
    return builder.as_markup()

def get_request_type_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа проблемы"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏫 Помещение/оборудование", callback_data="type_facility")
    )
    builder.row(
        InlineKeyboardButton(text="📚 Учебный процесс", callback_data="type_education")
    )
    builder.row(
        InlineKeyboardButton(text="👥 Персонал", callback_data="type_staff")
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_main")
    )
    return builder.as_markup()

def get_admin_action_keyboard(request_id: int) -> InlineKeyboardMarkup:
    """Кнопка для админа - взяться за работу"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Взяться за работу",
            callback_data=f"take_request_{request_id}"
        )
    )
    return builder.as_markup()

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Кнопка отмены"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel")
    )
    return builder.as_markup()

