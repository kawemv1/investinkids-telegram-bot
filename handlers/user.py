from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards.inline_kb import (
    get_main_menu, 
    get_request_type_keyboard,
    get_cancel_keyboard,
    get_admin_action_keyboard
)
from db.queries import save_report, get_report, get_user_reports
from config import ADMIN_GROUP_ID

router = Router()

# States for user report flow
class ReportStates(StatesGroup):
    waiting_for_report_type = State()
    waiting_for_message = State()

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

@router.callback_query(F.data == "back_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    """Return to main menu"""
    await state.clear()
    await callback.message.edit_text(
        "Выберите действие:",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@router.callback_query(F.data == "report_problem")
async def report_problem(callback: CallbackQuery, state: FSMContext):
    """Handle problem report"""
    await state.update_data(report_category="problem")
    await callback.message.edit_text(
        "🔧 Выберите тип проблемы:",
        reply_markup=get_request_type_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "suggestion")
async def suggestion(callback: CallbackQuery, state: FSMContext):
    """Handle suggestion"""
    await state.update_data(report_category="suggestion", report_type="Предложение")
    await callback.message.edit_text(
        "💡 Напишите ваше предложение:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(ReportStates.waiting_for_message)
    await callback.answer()

@router.callback_query(F.data == "feedback")
async def feedback(callback: CallbackQuery, state: FSMContext):
    """Handle feedback"""
    await state.update_data(report_category="feedback", report_type="Обратная связь")
    await callback.message.edit_text(
        "💬 Напишите вашу обратную связь:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(ReportStates.waiting_for_message)
    await callback.answer()

@router.callback_query(F.data.startswith("type_"))
async def select_report_type(callback: CallbackQuery, state: FSMContext):
    """Handle report type selection"""
    type_map = {
        "type_facility": "Помещение/оборудование",
        "type_education": "Учебный процесс",
        "type_staff": "Персонал"
    }
    
    report_type = type_map.get(callback.data)
    await state.update_data(report_type=report_type)
    
    await callback.message.edit_text(
        f"📝 Выбрано: {report_type}\n\n"
        "Опишите проблему подробно:",
        reply_markup=get_cancel_keyboard()
    )
    await state.set_state(ReportStates.waiting_for_message)
    await callback.answer()

@router.callback_query(F.data == "cancel")
async def cancel_report(callback: CallbackQuery, state: FSMContext):
    """Cancel current operation"""
    await state.clear()
    await callback.message.edit_text(
        "❌ Операция отменена.\n\nВыберите действие:",
        reply_markup=get_main_menu()
    )
    await callback.answer()

@router.message(ReportStates.waiting_for_message)
async def process_report_message(message: Message, state: FSMContext, bot: Bot):
    """Process user's report message"""
    data = await state.get_data()
    report_type = data.get('report_type')
    
    # Save to database
    report_id = save_report(
        user_id=message.from_user.id,
        user_name=message.from_user.full_name,
        report_type=report_type,
        report_text=message.text
    )
    
    # Send to user confirmation
    await message.answer(
        f"✅ Ваше обращение #{report_id} принято!\n\n"
        f"📌 Тип: {report_type}\n"
        f"📊 Статус: Ожидает обработки\n\n"
        "Мы свяжемся с вами в ближайшее время.",
        reply_markup=get_main_menu()
    )
    
    # Send to admin group
    admin_message = (
        f"🔔 НОВОЕ ОБРАЩЕНИЕ #{report_id}\n\n"
        f"👤 От: {message.from_user.full_name} (@{message.from_user.username or 'без username'})\n"
        f"🆔 User ID: {message.from_user.id}\n"
        f"📌 Тип: {report_type}\n"
        f"📊 Статус: Pending\n\n"
        f"💬 Сообщение:\n{message.text}\n\n"
        f"⏰ Время: {message.date.strftime('%d.%m.%Y %H:%M')}"
    )
    
    await bot.send_message(
        chat_id=ADMIN_GROUP_ID,
        text=admin_message,
        reply_markup=get_admin_action_keyboard(report_id)
    )
    
    await state.clear()

@router.callback_query(F.data == "my_requests")
async def my_reports(callback: CallbackQuery):
    """Show user's reports"""
    user_id = callback.from_user.id
    reports = get_user_reports(user_id)
    
    if not reports:
        await callback.answer("У вас пока нет обращений", show_alert=True)
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
    
    await callback.message.edit_text(
        reports_text,
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "view_report_")
async def view_report_details(callback: CallbackQuery):
    """View detailed report information"""
    report_id = int(callback.data.split("_")[2])
    report = get_report(report_id)
    
    if not report:
        await callback.answer("❌ Обращение не найдено", show_alert=True)
        return
    
    # Check if user owns this report
    if report['user_id'] != callback.from_user.id:
        await callback.answer("❌ Это не ваше обращение", show_alert=True)
        return
    
    status_text = {
        'pending': '⏳ Ожидает обработки',
        'in_progress': '🔄 В работе',
        'completed': '✅ Выполнено'
    }.get(report['status'], '❓ Неизвестно')
    
    details = (
        f"📋 Обращение #{report['id']}\n\n"
        f"📌 Тип: {report['report_type']}\n"
        f"📊 Статус: {status_text}\n"
        f"⏰ Создано: {report['created_at'].strftime('%d.%m.%Y %H:%M')}\n\n"
        f"💬 Ваше сообщение:\n{report['report_text']}\n"
    )
    
    if report['responsible_user_name']:
        details += f"\n👤 Ответственный: {report['responsible_user_name']}\n"
    
    if report['taken_at']:
        details += f"🕐 Взято в работу: {report['taken_at'].strftime('%d.%m.%Y %H:%M')}\n"
    
    if report['admin_response']:
        details += f"\n🔧 Ответ:\n{report['admin_response']}\n"
    
    if report['completed_at']:
        details += f"\n✅ Завершено: {report['completed_at'].strftime('%d.%m.%Y %H:%M')}"
    
    await callback.message.edit_text(details, reply_markup=get_cancel_keyboard())
    await callback.answer()
