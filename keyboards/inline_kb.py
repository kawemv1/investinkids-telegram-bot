from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_admin_take_report_keyboard(report_id: int) -> InlineKeyboardMarkup:
    """Inline-клавиатура для принятия жалобы админом"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Взять в работу",
            callback_data=f"take_{report_id}"
        )
    )
    return builder.as_markup()

def get_confirm_report_keyboard() -> InlineKeyboardMarkup:
    """Inline-клавиатура для подтверждения отправки жалобы"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Отправить жалобу",
            callback_data="confirm_report"
        ),
        InlineKeyboardButton(
            text="❌ Отменить",
            callback_data="cancel_report"
        )
    )
    return builder.as_markup()

def get_admin_complete_report_keyboard(report_id: int) -> InlineKeyboardMarkup:
    """Inline-клавиатура для завершения обращения админом"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Завершить обращение",
            callback_data=f"complete_{report_id}"
        )
    )
    return builder.as_markup()

