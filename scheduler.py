import asyncio
from datetime import datetime, timedelta
from aiogram import Bot
from db.queries import get_old_pending_reports
from config import ADMIN_GROUP_ID

# Store IDs of reports that already got reminders
reminded_reports = set()

async def check_pending_reports(bot: Bot):
    """Check for reports pending more than 1 hour"""
    while True:
        try:
            # Get reports older than 1 hour
            old_reports = get_old_pending_reports(hours=1)
            
            for report in old_reports:
                # Skip if already reminded
                if report['id'] in reminded_reports:
                    continue
                
                # Calculate time since creation
                time_diff = datetime.now() - report['created_at']
                hours = time_diff.seconds // 3600
                minutes = (time_diff.seconds % 3600) // 60
                
                # Send reminder
                reminder_message = (
                    f"⚠️ НАПОМИНАНИЕ: Обращение без ответа уже {hours}ч {minutes}м!\n\n"
                    f"📋 Обращение #{report['id']}\n"
                    f"⏰ Создано: {report['created_at'].strftime('%d.%m.%Y %H:%M')}\n\n"
                    f"👤 От: {report['user_name']}\n"
                    f"📌 Тип: {report['report_type']}\n"
                    f"💬 Сообщение:\n{report['report_text'][:150]}...\n\n"
                    f"❗ Пожалуйста, возьмите обращение в работу!\n"
                    f"Используйте команду: /take_{report['id']}"
                )
                
                if report.get('photo_file_id'):
                    await bot.send_photo(
                        chat_id=ADMIN_GROUP_ID,
                        photo=report['photo_file_id'],
                        caption=reminder_message
                    )
                else:
                    await bot.send_message(
                        chat_id=ADMIN_GROUP_ID,
                        text=reminder_message
                    )
                
                # Mark as reminded
                reminded_reports.add(report['id'])
                
                # Wait between reminders
                await asyncio.sleep(5)
            
            # Clear reminded reports older than 24 hours
            if len(reminded_reports) > 100:
                reminded_reports.clear()
                
        except Exception as e:
            print(f"❌ Error in scheduler: {e}")
        
        # Check every 30 minutes
        await asyncio.sleep(1800)

async def start_scheduler(bot: Bot):
    """Start the background scheduler"""
    asyncio.create_task(check_pending_reports(bot))
    print("✅ Reminder scheduler started - checking every 30 minutes")


async def start_scheduler(bot: Bot):
    """Start the background scheduler"""
    asyncio.create_task(check_pending_reports(bot))
    print("✅ Reminder scheduler started - checking every 30 minutes")
