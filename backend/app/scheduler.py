from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import or_
from . import models
from .database import SessionLocal
import datetime
from pywebpush import webpush
import json

VAPID_PRIVATE_KEY_PATH = "/home/user1/habits_project/vapid_private.pem"
VAPID_CLAIM_EMAIL = "mailto:ars.annaklychev@google.com"

def send_reminders():
    print(f"[Scheduler] tick at {datetime.datetime.now()}")
    db = SessionLocal()
    try:
        now = datetime.datetime.now()
        current_weekday = now.strftime("%a").lower()
        # Совпадение по часу и минуте (секунды в БД и у datetime.now() редко совпадают)
        habits = db.query(models.Habit).filter(
            models.Habit.reminder_time.isnot(None),
            models.Habit.reminder_time >= datetime.time(now.hour, now.minute, 0),
            models.Habit.reminder_time < datetime.time(now.hour, now.minute, 59, 999999),
            or_(
                models.Habit.days_of_week.is_(None),
                models.Habit.days_of_week == "",
                models.Habit.days_of_week.contains(current_weekday),
            ),
        ).all()
        for habit in habits:
            # Получаем активные подписки пользователя
            subscriptions = db.query(models.PushSubscription).filter(
                models.PushSubscription.user_id == habit.user_id
            ).all()
            for sub in subscriptions:
                print(f"[Scheduler] sending to {sub.endpoint[:50]}...")
                subscription_info = {
                    "endpoint": sub.endpoint,
                    "keys": {
                        "auth": sub.keys.get("auth"),
                        "p256dh": sub.keys.get("p256dh")
                    }
                }
                payload = json.dumps({
                    "title": "Напоминание о привычке",
                    "body": f"Пора выполнить: {habit.name}"
                })
                try:
                    webpush(
                        subscription_info=subscription_info,
                        data=payload,
                        vapid_private_key=VAPID_PRIVATE_KEY_PATH,
                        vapid_claims={"sub": VAPID_CLAIM_EMAIL}
                    )
                    print(f"Уведомление отправлено для привычки {habit.id}")
                except Exception as e:
                    print(f"Ошибка отправки: {e}")
                    # Если подписка недействительна, удаляем её
                    if "410" in str(e):
                        db.delete(sub)
                        db.commit()
    finally:
        db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(send_reminders, 'interval', minutes=1)
scheduler.start()
print("Scheduler started")