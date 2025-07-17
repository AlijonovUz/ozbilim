from django.contrib.sessions.models import Session


def logout_other_devices(user):
    ''' Berilgan foydalanuvchidagi tegishli barcha eski sessiyalar o'chiriladi. '''
    for session in Session.objects.all():
        data = session.get_decoded()
        if data.get('_auth_user_id') == str(user.id):
            session.delete()