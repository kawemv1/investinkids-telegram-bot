from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from db.queries import take_report, complete_report, get_report, get_reports_by_status

router = Router()

# States for admin response flow
class AdminStates(StatesGroup):
    waiting_for_response = State()

@router.callback_query(F.data.startswith("take_request_"))
async def take_request(callback: CallbackQuery, state: FSMContext):
    """Admin takes responsibility for report"""
    report_id = int(callback.data.split("_")[2])
    
    # Get report details
    report = get_report(report_id)
    
    if not report:
        await callback.answer("❌ Обращение не найдено", show_alert=True)
        return
    
    if report['status'] != 'pending':
        await callback.answer(
            f"⚠️ Обращение уже взято в работу: {report['responsible_user_name']}",
            show_alert=True
        )
        return
    
    # Assign admin to report
    take_report(
        report_id=report_id,
        worker_id=callback.from_user.id,
        worker_name=callback.from_user.full_name
    )
    
    # Update message in group
    await callback.message.edit_text(
        callback.message.text + f"\n\n✅ Взял(а) в работу: {callback.from_user.full_name}\n"
        f"🕐 Время: {callback.message.date.strftime('%d.%m.%Y %H:%M')}",
        reply_markup=None
    )
    
    # Send to admin in PM
    await callback.bot.send_message(
        chat_id=callback.from_user.id,
        text=(
            f"✅ Вы взяли обращение #{report_id} в работу\n\n"
            f"👤 От: {report['user_name']}\n"
            f"🆔 User ID: {report['user_id']}\n"
            f"📌 Тип: {report['report_type']}\n"
            f"💬 Сообщение:\n{report['report_text']}\n\n"
            f"📊 Статус: В работе\n"
            f"⏰ Создано: {report['created_at'].strftime('%d.%m.%Y %H:%M')}\n\n"
            f"Когда выполните работу, отправьте ответ:\n"
            f"/complete_{report_id} [ваш ответ]\n\n"
            f"Пример:\n"
            f"/complete_{report_id} Проблема решена, заменили оборудование"
        )
    )
    
    await callback.answer("✅ Обращение назначено вам")

@router.message(F.text.startswith("/complete_"))
async def complete_command(message: Message, state: FSMContext):
    """Admin completes report with response"""
    try:
        parts = message.text.split(" ", 1)
        report_id = int(parts[0].split("_")[1])
        
        if len(parts) < 2:
            await message.answer(
                "❌ Укажите ответ после команды:\n\n"
                f"Формат:\n"
                f"/complete_{report_id} [ваш ответ]\n\n"
                f"Пример:\n"
                f"/complete_{report_id} Проблема решена, заменили оборудование"
            )
            return
        
        admin_response = parts[1]
        
        # Get report
        report = get_report(report_id)
        
        if not report:
            await message.answer("❌ Обращение не найдено")
            return
        
        if report['status'] == 'completed':
            await message.answer(
                f"⚠️ Обращение #{report_id} уже завершено\n"
                f"Завершил: {report['responsible_user_name']}\n"
                f"Время: {report['completed_at'].strftime('%d.%m.%Y %H:%M')}"
            )
            return
        
        if report['responsible_user_id'] != message.from_user.id:
            await message.answer(
                f"❌ Вы не ответственный за это обращение\n"
                f"Ответственный: {report['responsible_user_name']}"
            )
            return
        
        # Complete report
        complete_report(report_id, admin_response)
        
        # Notify admin
        await message.answer(
            f"✅ Обращение #{report_id} завершено!\n\n"
            f"📌 Тип: {report['report_type']}\n"
            f"👤 От: {report['user_name']}\n"
            f"💬 Проблема: {report['report_text'][:100]}...\n\n"
            f"🔧 Ваш ответ: {admin_response}\n\n"
            "Пользователь получил уведомление. ✉️"
        )
        
        # Notify user
        await message.bot.send_message(
            chat_id=report['user_id'],
            text=(
                f"✅ Ваше обращение #{report_id} выполнено!\n\n"
                f"📌 Тип: {report['report_type']}\n"
                f"⏰ Создано: {report['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
                f"✓ Завершено: Сейчас\n\n"
                f"💬 Ваше сообщение:\n{report['report_text']}\n\n"
                f"🔧 Ответ ({report['responsible_user_name']}):\n{admin_response}\n\n"
                "Спасибо за обращение! 🙏"
            )
        )
        
    except (IndexError, ValueError) as e:
        await message.answer(
            "❌ Неверный формат команды\n\n"
            "Используйте:\n"
            "/complete_[ID] [ваш ответ]"
        )

@router.message(F.text == "/pending")
async def show_pending_reports(message: Message):
    """Show all pending reports (admin command)"""
    pending = get_reports_by_status('pending')
    
    if not pending:
        await message.answer("✅ Нет ожидающих обращений")
        return
    
    text = f"⏳ Ожидающие обращения ({len(pending)}):\n\n"
    
    for report in pending[:20]:  # Show max 20
        text += (
            f"📋 #{report['id']} - {report['report_type']}\n"
            f"👤 {report['user_name']}\n"
            f"⏰ {report['created_at'].strftime('%d.%m %H:%M')}\n"
            f"💬 {report['report_text'][:50]}...\n\n"
        )
    
    await message.answer(text)

@router.message(F.text == "/inprogress")
async def show_inprogress_reports(message: Message):
    """Show all in-progress reports (admin command)"""
    in_progress = get_reports_by_status('in_progress')
    
    if not in_progress:
        await message.answer("ℹ️ Нет обращений в работе")
        return
    
    text = f"🔄 В работе ({len(in_progress)}):\n\n"
    
    for report in in_progress[:20]:
        text += (
            f"📋 #{report['id']} - {report['report_type']}\n"
            f"👤 Пользователь: {report['user_name']}\n"
            f"👨‍💼 Ответственный: {report['responsible_user_name']}\n"
            f"🕐 Взято: {report['taken_at'].strftime('%d.%m %H:%M')}\n\n"
        )
    
    await message.answer(text)

@router.message(F.text == "/completed")
async def show_completed_reports(message: Message):
    """Show recently completed reports (admin command)"""
    completed = get_reports_by_status('completed')
    
    if not completed:
        await message.answer("ℹ️ Нет завершенных обращений")
        return
    
    text = f"✅ Завершено ({len(completed)}):\n\n"
    
    for report in completed[:15]:  # Show last 15
        text += (
            f"📋 #{report['id']} - {report['report_type']}\n"
            f"👤 Пользователь: {report['user_name']}\n"
            f"👨‍💼 Выполнил: {report['responsible_user_name']}\n"
            f"✓ {report['completed_at'].strftime('%d.%m %H:%M')}\n\n"
        )
    
    await message.answer(text)

@router.message(F.text.startswith("/report_"))
async def view_report(message: Message):
    """View specific report details (admin command)"""
    try:
        report_id = int(message.text.split("_")[1])
        report = get_report(report_id)
        
        if not report:
            await message.answer("❌ Обращение не найдено")
            return
        
        status_emoji = {
            'pending': '⏳',
            'in_progress': '🔄',
            'completed': '✅'
        }.get(report['status'], '❓')
        
        status_text = {
            'pending': 'Ожидает',
            'in_progress': 'В работе',
            'completed': 'Завершено'
        }.get(report['status'], 'Неизвестно')
        
        details = (
            f"{status_emoji} Обращение #{report['id']}\n\n"
            f"👤 От: {report['user_name']}\n"
            f"🆔 User ID: {report['user_id']}\n"
            f"📌 Тип: {report['report_type']}\n"
            f"📊 Статус: {status_text}\n"
            f"⏰ Создано: {report['created_at'].strftime('%d.%m.%Y %H:%M')}\n\n"
            f"💬 Сообщение:\n{report['report_text']}\n"
        )
        
        if report['responsible_user_name']:
            details += f"\n👨‍💼 Ответственный: {report['responsible_user_name']}\n"
            details += f"🆔 ID: {report['responsible_user_id']}\n"
        
        if report['taken_at']:
            details += f"🕐 Взято в работу: {report['taken_at'].strftime('%d.%m.%Y %H:%M')}\n"
        
        if report['admin_response']:
            details += f"\n🔧 Ответ:\n{report['admin_response']}\n"
        
        if report['completed_at']:
            details += f"\n✅ Завершено: {report['completed_at'].strftime('%d.%m.%Y %H:%M')}"
        
        await message.answer(details)
        
    except (IndexError, ValueError):
        await message.answer("❌ Используйте: /report_[ID]")

@router.message(F.text == "/adminhelp")
async def admin_help(message: Message):
    """Show admin commands help"""
    help_text = (
        "🔧 Команды администратора:\n\n"
        "/pending - Показать ожидающие обращения\n"
        "/inprogress - Показать обращения в работе\n"
        "/completed - Показать завершенные\n"
        "/report_[ID] - Детали обращения\n"
        "/complete_[ID] [ответ] - Завершить обращение\n"
        "/adminhelp - Эта справка\n\n"
        "💡 Взять обращение в работу можно кнопкой в группе"
    )
    await message.answer(help_text)
