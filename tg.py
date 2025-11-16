from telegram import Bot, Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import CommandHandler, MessageHandler,  Updater, ApplicationBuilder, ContextTypes, InlineQueryHandler
from telegram.request import HTTPXRequest

import json
import requests
import os
import datetime
import wear
import schedule
import telegram
import booth

class TelegramBot:
    def __init__(self, token = None):
        if token is None:
            # Load token from config.json
            with open('config.json', 'r') as f:
                config = json.load(f)
                token = config.get('botToken')
        self.token = token
        
        # Create request with longer timeouts
        request = HTTPXRequest(
            connection_pool_size=8,
            connect_timeout=30.0,
            read_timeout=30.0,
            write_timeout=30.0,
            pool_timeout=30.0
        )
        
        self.application = ApplicationBuilder().token(self.token).request(request).build()
        self.application.add_handler(CommandHandler('hello', self.hello))
        self.application.add_handler(CommandHandler('wear', self.wear))
        self.application.add_handler(InlineQueryHandler(self.inline_query))
        print("Telegram Bot initialized.")
        self.application.run_polling()


    async def hello(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(f'Hello, {update.effective_user.first_name}!')

    async def wear(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        wear_instance = wear.Wear()
        today = datetime.date.today()
        today_wear, tomorrow_wear = wear_instance.get_wear_for_date(today)
        response_message = f"Wear for {today.strftime('%Y-%m-%d')}:\n"
        response_message += f"  Today: {today_wear if today_wear else 'you are free to choose'}\n"
        response_message += f"  Tomorrow: {tomorrow_wear if tomorrow_wear else 'you are free to choose'}"
        await update.message.reply_text(response_message)

    async def inline_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = (update.inline_query.query or "").strip()
        
        # Prepare all results
        results = []
        today = datetime.date.today()
        query_empty = not query
        
        if query_empty:
            # 1. Wear information
            wear_instance = wear.Wear()
            today_wear, tomorrow_wear = wear_instance.get_wear_for_date(today)
            
            wear_message = f"🎽 Wear Schedule for {today.strftime('%Y-%m-%d')}:\n\n"
            wear_message += f"Today: {today_wear if today_wear else 'you are free to choose'}\n"
            wear_message += f"Tomorrow: {tomorrow_wear if tomorrow_wear else 'you are free to choose'}"
            
            results.append(
                InlineQueryResultArticle(
                    id='wear_today',
                    title='👕 What to Wear Today',
                    input_message_content=InputTextMessageContent(wear_message),
                    description=f'Today: {today_wear if today_wear else "Free choice"}'
                )
            )
            
            # 2. Current shift information
            schedule_instance = schedule.Schedule()
            current_shift = schedule_instance.get_current_shift()
            last_shift = schedule_instance.get_last_shift()
            next_shift = schedule_instance.get_next_shift()
            
            def format_shift(shift_data):
                if shift_data is None:
                    return '<b>No shift</b>'
                value = shift_data.get_value()
                start_time = value['start_time']
                end_time = value['end_time']
                student1 = value['student1'].strip()
                student2 = value['student2'].strip()
                return f"{start_time}-{end_time}: <b>{student1}</b> & <b>{student2}</b>"


            shift_message = f"🕒 Current Shift Information:\n\n"
            shift_message += f"Last Shift: \n{format_shift(last_shift)}\n"
            shift_message += f"Current Shift:\n {format_shift(current_shift)}\n"
            shift_message += f"Next Shift: \n{format_shift(next_shift)}"

            results.append(
                InlineQueryResultArticle(
                    id='current_shift',
                    title='🕒 Current Shift Info',
                    input_message_content=InputTextMessageContent(shift_message, parse_mode='HTML'),
                    description='Last, current, and next shift'
                )
            )
            
            # 3. Today's full schedule
            shifts = schedule_instance.get_schedule_for_date(today)
            
            schedule_message = f"📅 Today's Shift Schedule ({today.strftime('%Y-%m-%d')}):\n\n"
            if shifts:
                for time_range, students in shifts.items():
                    student1 = students.get('student1', 'N/A')
                    student2 = students.get('student2', 'N/A')
                    schedule_message += f"{time_range}: <b>{student1}</b> & <b>{student2}</b>\n"
            else:
                schedule_message += "No shifts scheduled for today."
            
            results.append(
                InlineQueryResultArticle(
                    id='today_shift',
                    title="📅 Today's Full Schedule",
                    input_message_content=InputTextMessageContent(schedule_message, parse_mode='HTML'),
                    description="View all shifts for today"
                )
            )
        else:
            booth_instance = booth.Booth()
            booth_results = booth_instance.get_booth_numbers(query)
            booth_name = booth_instance.get_booth_name(query)
            
            if booth_results:     
                booth_message = f"🏢 Booth Information for '{query}':\n\n"
                for booth_entry in booth_results:
                    entry_name = booth_entry['boothName']
                    booth_numbers = ', '.join(booth_entry['boothNumbers'])
                    booth_message += f"Booth Name: <b>{entry_name}</b>\nBooth Numbers: {booth_numbers}\n\n"
                
                results.append(
                    InlineQueryResultArticle(
                        id='booth_info',
                        title=f"🏢 Booth Info for '{query}'",
                        input_message_content=InputTextMessageContent(booth_message, parse_mode='HTML'),
                        description=f'Booth information matching "{query}"'
                    )
                )

            if booth_name:
                booth_name_message = f"🏢 Booth Name for Number '{query}':\n\nBooth Name: <b>{booth_name}</b>"
                
                results.append(
                    InlineQueryResultArticle(
                        id='booth_name',
                        title=f"🏢 Booth Name for Number '{query}'",
                        input_message_content=InputTextMessageContent(booth_name_message, parse_mode='HTML'),
                        description=f'Booth name for number "{query}"'
                    )
                )

            if not booth_results and not booth_name:
                results.append(
                    InlineQueryResultArticle(
                        id='booth_not_found',
                        title=f"No Booth Found for '{query}'",
                        input_message_content=InputTextMessageContent(
                            f"Unable to find booth information for \"{query}\"."
                        ),
                        description='Try a different exhibitor name or booth number'
                    )
                )

        await update.inline_query.answer(results)

if __name__ == "__main__":
    bot = TelegramBot()
