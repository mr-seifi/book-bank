import requests
from secret import TELEGRAM_INFO_GROUP, TELEGRAM_WARNING_GROUP, TELEGRAM_ERROR_GROUP, TELEGRAM_FILES_CHANNEL, \
    TELEGRAM_BOT_TOKEN
from telegram.constants import ParseMode
from django import setup
from django.conf import settings
from telegram import Bot

setup()
from advertising.models import Advertiser


class InternalService:

    @staticmethod
    def get_bot():
        return Bot(token=TELEGRAM_BOT_TOKEN,
                   base_url='http://0.0.0.0:8081/bot')

    @staticmethod
    async def _send_message(context, message, to):
        bot = None
        if not context:
            bot = InternalService.get_bot()

        if bot:
            response = await bot.send_message(chat_id=to,
                                              text=message,
                                              parse_mode=ParseMode.MARKDOWN)
            return response.message_id

        try:
            response = await context.bot.send_message(chat_id=to,
                                                      text=message,
                                                      parse_mode=ParseMode.MARKDOWN)
        except RuntimeError:
            response = await context.send_message(chat_id=to,
                                                  text=message,
                                                  parse_mode=ParseMode.MARKDOWN)
        return response.message_id

    @staticmethod
    async def _send_file(context, file, filename, caption, **kwargs):
        response = await context.bot.send_document(chat_id=TELEGRAM_FILES_CHANNEL,
                                                   document=file,
                                                   filename=filename,
                                                   caption=caption,
                                                   write_timeout=500,
                                                   read_timeout=500,
                                                   connect_timeout=500,
                                                   pool_timeout=500,
                                                   **kwargs)
        return response.message_id

    @classmethod
    async def send_info(cls, context, info):
        response = await cls._send_message(context=context,
                                           message=settings.TELEGRAM_MESSAGES['info'].format(info=str(info)),
                                           to=TELEGRAM_INFO_GROUP)
        return response

    @classmethod
    async def send_warning(cls, context, warning):
        response = await cls._send_message(context=context,
                                           message=settings.TELEGRAM_MESSAGES['warning'].format(warning=str(warning)),
                                           to=TELEGRAM_WARNING_GROUP)
        return response

    @classmethod
    async def send_error(cls, context, error):
        if not context:
            context = InternalService.get_bot()

        response = await cls._send_message(context=context,
                                           message=settings.TELEGRAM_MESSAGES['error'].format(ex=str(error)),
                                           to=TELEGRAM_ERROR_GROUP)
        return response

    @classmethod
    async def send_file(cls, context, file, filename, description, **kwargs):
        """

        :param context:
        :param file:
        :param filename:
        :param description:
        :param kwargs: thumb
        :return:
        """
        response = await cls._send_file(context=context,
                                        file=file,
                                        filename=filename,
                                        caption=description,
                                        **kwargs)
        return response

    @staticmethod
    async def forward_file(context, file_id, to):
        response = await context.bot.forward_message(chat_id=to,
                                                     from_chat_id=TELEGRAM_FILES_CHANNEL,
                                                     message_id=file_id)
        return response

    @staticmethod
    async def send_monitoring(context, photo_path, caption):
        if context:
            response = await context.bot.send_photo(chat_id=TELEGRAM_WARNING_GROUP,
                                                    photo=photo_path,
                                                    caption=caption)
        else:
            bot = InternalService.get_bot()
            response = await bot.send_photo(chat_id=TELEGRAM_WARNING_GROUP,
                                            photo=photo_path,
                                            caption=caption)

        return response

    @classmethod
    def _is_user_joined_channel(cls, channel_id, user_id, session=None) -> bool:
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getChatMember?chat_id=@{channel_id}&user_id={user_id}'
        if not session:
            session = requests.Session()

        response = session.get(url)
        if not response.status_code == 200:
            return False

        status = response.json().get('result').get('status')
        if status == 'left':
            return False
        return True

    @classmethod
    def is_user_verified(cls, user_id) -> bool:
        with requests.Session() as session:
            for advertiser in Advertiser.objects.active():
                if not cls._is_user_joined_channel(channel_id=advertiser.channel_id,
                                                   user_id=user_id,
                                                   session=session):
                    return False

        return True

    @classmethod
    def should_join(cls, user_id) -> list:
        advertisers = []
        with requests.Session() as session:
            for advertiser in Advertiser.objects.active():
                if not cls._is_user_joined_channel(channel_id=advertiser.channel_id,
                                                   user_id=user_id,
                                                   session=session):
                    advertisers.append(advertiser)
        return advertisers
