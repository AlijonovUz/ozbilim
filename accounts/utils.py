import requests
from django.conf import settings

from django.core.files.base import ContentFile
from django.contrib.sessions.models import Session


def logout_other_devices(user):
    ''' Berilgan foydalanuvchidagi tegishli barcha eski sessiyalar o'chiriladi. '''
    for session in Session.objects.all():
        data = session.get_decoded()
        if data.get('_auth_user_id') == str(user.id):
            session.delete()


def getChat(chat_id):
    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getChat?chat_id={chat_id}"
    response = requests.get(url)

    return response.json()


def download_telegram_profile_photo(file_id, filename="avatar.jpg"):
    file_info_url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getFile?file_id={file_id}"
    file_info = requests.get(file_info_url).json()
    file_path = file_info['result']['file_path']
    file_url = f"https://api.telegram.org/file/bot{settings.BOT_TOKEN}/{file_path}"
    file_content = requests.get(file_url).content
    return ContentFile(file_content, name=filename)
