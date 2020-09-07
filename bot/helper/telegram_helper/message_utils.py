from pyrogram import Client
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
import time
import psutil
from bot import AUTO_DELETE_MESSAGE_DURATION, LOGGER, \
    status_reply_dict, status_reply_dict_lock, download_dict, download_dict_lock
from bot.helper.ext_utils.bot_utils import get_readable_message, get_readable_file_size, MirrorStatus


def sendMessage(text: str, bot: Client, message: Message):
    try:
        return bot.send_message(chat_id=message.chat.id,
                            reply_to_message_id=message.message_id,
                            text=text)
    except Exception as e:
        LOGGER.error(str(e))
        
def sendMarkup(text: str, bot: Client, message: Message, reply_markup: InlineKeyboardMarkup):
    try:
        return bot.send_message(chat_id=message.chat.id,
                             reply_to_message_id=message.message_id,
                             text=text, 
                             reply_markup=reply_markup, 
                             parse_mode='html')
    except Exception as e:
        LOGGER.error(str(e))


def editMessage(text: str, message: Message):
    try:
        message.edit_text(text)
    except Exception as e:
        LOGGER.error(str(e))


def deleteMessage(message: Message):
    try:
        message.delete()
    except Exception as e:
        LOGGER.error(str(e))


def sendLogFile(bot: Client, message: Message):
    f = 'log.txt'
    bot.send_document(
        document=f,
        reply_to_message_id=message.message_id,
        chat_id=message.chat.id
    )


def auto_delete_message(bot, cmd_message: Message, bot_message: Message):
    if AUTO_DELETE_MESSAGE_DURATION != -1:
        time.sleep(AUTO_DELETE_MESSAGE_DURATION)
        try:
            # Skip if None is passed meaning we don't want to delete bot or cmd message
            deleteMessage(cmd_message)
            deleteMessage(bot_message)
        except AttributeError:
            pass


def delete_all_messages():
    with status_reply_dict_lock:
        for message in list(status_reply_dict.values()):
            try:
                deleteMessage(message)
                del status_reply_dict[message.chat.id]
            except Exception as e:
                LOGGER.error(str(e))

        
def update_all_messages():
    msg = get_readable_message()
    msg += f"<b>CPU:</b> {psutil.cpu_percent()}%" \
           f" <b>DISK:</b> {psutil.disk_usage('/').percent}%" \
           f" <b>RAM:</b> {psutil.virtual_memory().percent}%"
    with download_dict_lock:
        dlspeed_bytes = 0
        uldl_bytes = 0
        for download in list(download_dict.values()):
            speedy = download.speed()
            if download.status() == MirrorStatus.STATUS_DOWNLOADING:
                if 'KiB/s' in speedy:
                    dlspeed_bytes += float(speedy.split('K')[0]) * 1024
                elif 'MiB/s' in speedy:
                    dlspeed_bytes += float(speedy.split('M')[0]) * 1048576 
            if download.status() == MirrorStatus.STATUS_UPLOADING:
                if 'KB/s' in speedy:
            	    uldl_bytes += float(speedy.split('K')[0]) * 1024
                elif 'MB/s' in speedy:
                    uldl_bytes += float(speedy.split('M')[0]) * 1048576
        dlspeed = get_readable_file_size(dlspeed_bytes)
        ulspeed = get_readable_file_size(uldl_bytes)
        msg += f"\n<b>DL:</b>{dlspeed}ps 🔻| <b>UL:</b>{ulspeed}ps 🔺\n"
    with status_reply_dict_lock:
        for chat_id in list(status_reply_dict.keys()):
            if status_reply_dict[chat_id] and msg != status_reply_dict[chat_id].text:
                if len(msg) == 0:
                    msg = "Starting DL"
                try:
                    editMessage(msg, status_reply_dict[chat_id])
                except Exception as e:
                    LOGGER.error(str(e))
                status_reply_dict[chat_id].text = msg


def sendStatusMessage(msg: Message, bot: Client):
    progress = get_readable_message()
    progress += f"<b>CPU:</b> {psutil.cpu_percent()}%" \
           f" <b>DISK:</b> {psutil.disk_usage('/').percent}%" \
           f" <b>RAM:</b> {psutil.virtual_memory().percent}%"
    with download_dict_lock:
        dlspeed_bytes = 0
        uldl_bytes = 0
        for download in list(download_dict.values()):
            speedy = download.speed()
            if download.status() == MirrorStatus.STATUS_DOWNLOADING:
                if 'KiB/s' in speedy:
                    dlspeed_bytes += float(speedy.split('K')[0]) * 1024
                elif 'MiB/s' in speedy:
                    dlspeed_bytes += float(speedy.split('M')[0]) * 1048576 
            if download.status() == MirrorStatus.STATUS_UPLOADING:
                if 'KB/s' in speedy:
            	    uldl_bytes += float(speedy.split('K')[0]) * 1024
                elif 'MB/s' in speedy:
                    uldl_bytes += float(speedy.split('M')[0]) * 1048576
        dlspeed = get_readable_file_size(dlspeed_bytes)
        ulspeed = get_readable_file_size(uldl_bytes)
        progress += f"\n<b>DL:</b>{dlspeed}ps 🔻| <b>UL:</b>{ulspeed}ps 🔺\n"
    with status_reply_dict_lock:
        if msg.chat.id in list(status_reply_dict.keys()):
            try:
                message = status_reply_dict[msg.chat.id]
                deleteMessage(bot, message)
                del status_reply_dict[msg.chat.id]
            except Exception as e:
                LOGGER.error(str(e))
                del status_reply_dict[msg.chat.id]
                pass
        if len(progress) == 0:
            progress = "Starting DL"
        message = sendMessage(progress, bot, msg)
        status_reply_dict[msg.chat.id] = message

