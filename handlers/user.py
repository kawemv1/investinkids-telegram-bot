from aiogram import Router, F, Bot
from aiogram.types import Message, PhotoSize, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.reply_kb import (
    get_main_menu, 
    get_request_type_keyboard,
    get_cancel_keyboard,
    get_photo_choice_keyboard
)
from keyboards.inline_kb import get_confirm_report_keyboard, get_admin_take_report_keyboard
from db.queries import save_report, get_report, get_user_reports
from config import ADMIN_GROUP_ID

router = Router()

# States for user report flow
class ReportStates(StatesGroup):
    waiting_for_report_type = State()
    waiting_for_photo_choice = State()
    waiting_for_photo = State()
    waiting_for_message = State()
    waiting_for_confirm = State()  # New state for confirmation

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Start command - show main menu"""
    await message.answer(
        f"👋 Здравствуйте, {message.from_user.first_name}!\n\n"
        "Добро пожаловать в систему обратной связи InvestInKids.\n\n"
        "Вы можете:\n"
        "• Сообщить о проблеме\n"
        "• Оставить предложение\n"
        "• Дать обратную связь\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu()
    )

@router.message(F.text == "🔙 Назад")
async def back_to_main(message: Message, state: FSMContext):
    """Return to main menu"""
    await state.clear()
    await message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu()
    )

@router.message(F.text == "🔧 Сообщить о проблеме")
async def report_problem(message: Message, state: FSMContext):
    """Handle problem report"""
    await state.update_data(report_category="problem")
    await message.answer(
        "🔧 Выберите тип проблемы:",
        reply_markup=get_request_type_keyboard()
    )

@router.message(F.text == "💡 Оставить предложение")
async def suggestion(message: Message, state: FSMContext):
    """Handle suggestion"""
    await state.update_data(report_category="suggestion", report_type="Предложение")
    await message.answer(
        "💡 Хотите добавить фото к предложению?",
        reply_markup=get_photo_choice_keyboard()
    )
    await state.set_state(ReportStates.waiting_for_photo_choice)

@router.message(F.text == "💬 Обратная связь")
async def feedback(message: Message, state: FSMContext):
    """Handle feedback"""
    await state.update_data(report_category="feedback", report_type="Обратная связь")
    await message.answer(
        "💬 Хотите добавить фото к обратной связи?",
        reply_markup=get_photo_choice_keyboard()
    )
    await state.set_state(ReportStates.waiting_for_photo_choice)

@router.message(F.text.in_(["🏫 Помещение/оборудование", "📚 Учебный процесс", "👥 Персонал"]))
async def select_report_type(message: Message, state: FSMContext):
    """Handle report type selection"""
    type_map = {
        "🏫 Помещение/оборудование": "Помещение/оборудование",
        "📚 Учебный процесс": "Учебный процесс",
        "👥 Персонал": "Персонал"
    }
    
    report_type = type_map.get(message.text)
    await state.update_data(report_type=report_type)
    
    await message.answer(
        f"📝 Выбрано: {report_type}\n\n"
        "Хотите добавить фото к жалобе?",
        reply_markup=get_photo_choice_keyboard()
    )
    await state.set_state(ReportStates.waiting_for_photo_choice)

@router.message(ReportStates.waiting_for_photo_choice, F.text == "📷 Добавить фото")
async def request_photo(message: Message, state: FSMContext):
    """Request photo from user"""
    await message.answer(
        "📷 Пожалуйста, отправьте фото:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(ReportStates.waiting_for_photo)

@router.message(ReportStates.waiting_for_photo_choice, F.text == "➡️ Продолжить без фото")
async def skip_photo(message: Message, state: FSMContext):
    """Skip photo and request message"""
    data = await state.get_data()
    report_type = data.get('report_type', 'Обращение')
    
    await message.answer(
        f"📝 Теперь опишите проблему подробно:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(ReportStates.waiting_for_message)

@router.message(ReportStates.waiting_for_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    """Process photo from user"""
    # Get the largest photo
    photo: PhotoSize = message.photo[-1]
    photo_file_id = photo.file_id
    
    await state.update_data(photo_file_id=photo_file_id)
    
    data = await state.get_data()
    report_type = data.get('report_type', 'Обращение')
    
    await message.answer(
        f"✅ Фото получено!\n\n"
        f"📝 Теперь опишите проблему подробно:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(ReportStates.waiting_for_message)

@router.message(ReportStates.waiting_for_photo)
async def invalid_photo(message: Message):
    """Handle invalid photo input"""
    await message.answer(
        "❌ Пожалуйста, отправьте фото или нажмите 'Отменить'",
        reply_markup=get_cancel_keyboard()
    )

@router.message(F.text == "❌ Отменить")
async def cancel_report(message: Message, state: FSMContext):
    """Cancel current operation"""
    await state.clear()
    await message.answer(
        "❌ Операция отменена.\n\nВыберите действие:",
        reply_markup=get_main_menu()
    )

@router.message(ReportStates.waiting_for_message)
async def process_report_message(message: Message, state: FSMContext):
    """Process user's report message and show preview"""
    data = await state.get_data()
    report_type = data.get('report_type')
    photo_file_id = data.get('photo_file_id')
    
    # Save message text to state
    await state.update_data(report_text=message.text)
    
    # Show preview
    preview_text = (
        f"📋 Предпросмотр обращения:\n\n"
        f"📌 Тип: {report_type}\n"
    )
    
    if photo_file_id:
        preview_text += "📷 Фото: прикреплено\n"
    
    preview_text += (
        f"💬 Сообщение:\n{message.text}\n\n"
        f"Проверьте информацию и нажмите 'Отправить жалобу' для отправки."
    )
    
    if photo_file_id:
        await message.answer_photo(
            photo=photo_file_id,
            caption=preview_text,
            reply_markup=get_confirm_report_keyboard()
        )
    else:
        await message.answer(
            preview_text,
            reply_markup=get_confirm_report_keyboard()
        )
    
    await state.set_state(ReportStates.waiting_for_confirm)

@router.callback_query(F.data == "confirm_report", ReportStates.waiting_for_confirm)
async def confirm_report_callback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """Confirm and send report"""
    data = await state.get_data()
    report_type = data.get('report_type')
    photo_file_id = data.get('photo_file_id')
    report_text = data.get('report_text')
    
    # Save to database
    report_id = save_report(
        user_id=callback.from_user.id,
        user_name=callback.from_user.full_name,
        report_type=report_type,
        report_text=report_text,
        photo_file_id=photo_file_id
    )
    
    # Send to user confirmation
    confirmation_text = (
        f"✅ Ваше обращение #{report_id} принято!\n\n"
        f"📌 Тип: {report_type}\n"
        f"📊 Статус: Ожидает обработки\n\n"
    )
    
    if photo_file_id:
        confirmation_text += "📷 Фото прикреплено\n\n"
    
    confirmation_text += "Мы свяжемся с вами в ближайшее время."
    
    # Update message (handle both photo and text messages)
    if callback.message.photo:
        await callback.message.edit_caption(
            caption=confirmation_text,
            reply_markup=None
        )
    else:
        await callback.message.edit_text(
            text=confirmation_text,
            reply_markup=None
        )
    
    await callback.answer("✅ Обращение отправлено!")
    
    # Get current time for the message
    from datetime import datetime
    current_time = datetime.now().strftime('%d.%m.%Y %H:%M')
    
    # Send to admin group with inline button
    admin_message = (
        f"🔔 НОВОЕ ОБРАЩЕНИЕ #{report_id}\n\n"
        f"👤 От: {callback.from_user.full_name} (@{callback.from_user.username or 'без username'})\n"
        f"🆔 User ID: {callback.from_user.id}\n"
        f"📌 Тип: {report_type}\n"
        f"📊 Статус: Pending\n\n"
        f"💬 Сообщение:\n{report_text}\n\n"
        f"⏰ Время: {current_time}"
    )
    
    # Send to admin group with inline button
    import logging
    logger = logging.getLogger(__name__)
    
    if not ADMIN_GROUP_ID:
        logger.error("ADMIN_GROUP_ID is not set! Cannot send report to admin group.")
        await callback.answer("⚠️ Ошибка: группа администраторов не настроена", show_alert=True)
    else:
        try:
            logger.info(f"Sending report #{report_id} to admin group {ADMIN_GROUP_ID}")
            
            if photo_file_id:
                # Send message with photo and inline button
                sent_message = await bot.send_photo(
                    chat_id=ADMIN_GROUP_ID,
                    photo=photo_file_id,
                    caption=admin_message,
                    reply_markup=get_admin_take_report_keyboard(report_id)
                )
                logger.info(f"Report #{report_id} sent to admin group successfully (with photo), message_id: {sent_message.message_id}")
            else:
                # Send text message with inline button
                sent_message = await bot.send_message(
                    chat_id=ADMIN_GROUP_ID,
                    text=admin_message,
                    reply_markup=get_admin_take_report_keyboard(report_id)
                )
                logger.info(f"Report #{report_id} sent to admin group successfully (text only), message_id: {sent_message.message_id}")
        except Exception as e:
            # Log error but don't fail the user flow
            logger.error(f"Failed to send message to admin group {ADMIN_GROUP_ID}: {e}", exc_info=True)
            # Still send confirmation to user, but notify about error
            await bot.send_message(
                chat_id=callback.from_user.id,
                text=f"⚠️ Обращение #{report_id} сохранено, но не удалось отправить в группу администраторов. Обратитесь к администратору."
            )
    
    await state.clear()
    
    # Send main menu to user
    await bot.send_message(
        chat_id=callback.from_user.id,
        text="Выберите действие:",
        reply_markup=get_main_menu()
    )

@router.callback_query(F.data == "cancel_report", ReportStates.waiting_for_confirm)
async def cancel_report_callback(callback: CallbackQuery, state: FSMContext):
    """Cancel report sending"""
    await state.clear()
    
    # Update message (handle both photo and text messages)
    if callback.message.photo:
        await callback.message.edit_caption(
            caption="❌ Отправка обращения отменена.",
            reply_markup=None
        )
    else:
        await callback.message.edit_text(
            text="❌ Отправка обращения отменена.",
            reply_markup=None
        )
    
    await callback.answer("❌ Отправка отменена")
    
    # Send main menu
    await callback.message.answer(
        "Выберите действие:",
        reply_markup=get_main_menu()
    )

@router.message(F.text == "📋 Мои обращения")
async def my_reports(message: Message):
    """Show user's reports"""
    user_id = message.from_user.id
    reports = get_user_reports(user_id)
    
    if not reports:
        await message.answer(
            "У вас пока нет обращений",
            reply_markup=get_main_menu()
        )
        return
    
    # Format reports list
    reports_text = "📋 Ваши обращения:\n\n"
    
    for report in reports[:10]:  # Show last 10 reports
        status_emoji = {
            'pending': '⏳',
            'in_progress': '🔄',
            'completed': '✅'
        }.get(report['status'], '❓')
        
        status_text = {
            'pending': 'Ожидает',
            'in_progress': 'В работе',
            'completed': 'Выполнено'
        }.get(report['status'], 'Неизвестно')
        
        reports_text += (
            f"{status_emoji} Обращение #{report['id']}\n"
            f"Тип: {report['report_type']}\n"
            f"Статус: {status_text}\n"
        )
        
        if report['responsible_user_name']:
            reports_text += f"Ответственный: {report['responsible_user_name']}\n"
        
        if report['completed_at']:
            reports_text += f"Завершено: {report['completed_at'].strftime('%d.%m.%Y %H:%M')}\n"
        
        reports_text += "\n"
    
    await message.answer(
        reports_text,
        reply_markup=get_main_menu()
    )

@router.message(F.text & ~F.text.startswith("/") & (F.chat.type == "private"))
async def fallback_handler(message: Message, state: FSMContext):
    """Fallback handler for unknown messages (only for non-command text messages in private chat)"""
    current_state = await state.get_state()
    
    # Если пользователь в процессе создания обращения
    if current_state:
        await message.answer(
            "❌ Пожалуйста, следуйте инструкциям выше или нажмите '❌ Отменить' для возврата в главное меню.",
            reply_markup=get_cancel_keyboard()
        )
    else:
        # Если пользователь просто отправил неизвестное сообщение
        await message.answer(
            "❓ Я не понимаю эту команду.\n\n"
            "Используйте кнопки меню или команду /start для начала работы.",
            reply_markup=get_main_menu()
        )
