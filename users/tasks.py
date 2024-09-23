from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from sitegames import settings

User = get_user_model()
def send_birthday_email(user):
    subject = "С Днем Рождения!"
    message = f"Дорогой {user.first_name}, поздравляем вас с Днем Рождения!"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)


@shared_task
def send_birthday_greetings():
    today = timezone.localdate()

    birthday_users = User.objects.all()

    for user in birthday_users:
        print(user)
        print(user.date_birth)
        print(today)
        if user.date_birth and user.date_birth.month == today.month and user.date_birth.day == today.day:
            print(1)
            send_birthday_email(user)