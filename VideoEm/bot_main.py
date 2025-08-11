import requests
import os

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, KeyboardButton, \
    ReplyKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes, filters, Application, MessageHandler, CallbackQueryHandler

BOT_TOKEN = os.environ.get('BOT_TOKEN')

web_app = WebAppInfo(url='<WEB_APP_URL>')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command.
    Displays a welcome message and provides options to open the app or upload a video.
    """
    start_button = KeyboardButton('/start')
    reply_keyboard = ReplyKeyboardMarkup([[start_button]], resize_keyboard=True, is_persistent=True)
    await update.message.reply_text('Welcome to VideoEm App', reply_markup=reply_keyboard)

    keyboard = [[InlineKeyboardButton("Open App", web_app=web_app)],
                [InlineKeyboardButton("Upload Video", callback_data='upload')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("What would you like to do?", reply_markup=reply_markup, )


async def inline_button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Wait for upload video to proceed
    """
    query = update.callback_query
    await query.answer()
    chat_id = update.effective_chat.id
    if query.data == 'upload':
        await context.bot.send_message(chat_id=chat_id, text="Please send video file to this chat. Video must be more "
                                                             "than 5 sec duration and its size must be less 20Mb") 
        context.user_data['awaiting_video'] = True


async def receive_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle video uploads and send data to the app server
    """
    if context.user_data.get('awaiting_video'):
        video = update.message.video
        user_id = update.message.from_user.id
        video_upload_endpoint = web_app.url + 'api/v1/video_add'

        if video:
            context.user_data['awaiting_video'] = False
            try:
                response = requests.post(video_upload_endpoint,
                                         json={'user_id': user_id, 'video_id': video.file_id})
                print({'user_id': user_id, 'video_id': video.file_id})
                response.raise_for_status()

                if response.json()['result']:
                    await update.message.reply_text(text=f"{response.json()['result']} You may add title, description "
                                                         f"and tags through VideoEmApp -> Account -> My Videos -> Double"
                                                         f" click on video")
                else:
                    await update.message.reply_text(text="Please, enter to the app once for user account registration")
            except requests.exceptions.RequestException as e:
                await update.message.reply_text(
                    text=f"An error '{e}' occurred while processing your request. Please try again later.")
        else:
            await update.message.reply_text("It seems like you haven't uploaded a video file. Please try again.")


def main():
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(inline_button_click))
    application.add_handler(MessageHandler(filters.VIDEO, receive_video))

    print("Bot is running... Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
