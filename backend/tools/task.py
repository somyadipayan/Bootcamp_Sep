# Tasks are methods or any jobs that are needed to run asynchronously (by celery) 
# in the background or if we want a method to be scheduled

from tools.workers import celery
from models import *
from celery.schedules import crontab

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab(hour = 10, minute= 00), send_daily_email.s(), name="Send email every 10 seconds")


@celery.task
def sendHi(userid):
    user = User.query.filter_by(id=userid).first()
    return "Hi " + user.username

@celery.task
def add():
    return 3+4

@celery.task
def send_daily_email():
    users = User.query.all()
    for user in users:
        print(f"Sending email to user {user.username}")
    return "Emails sent"