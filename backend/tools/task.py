# Tasks are methods or any jobs that are needed to run asynchronously (by celery) 
# in the background or if we want a method to be scheduled

from tools.workers import celery
from models import *
from celery.schedules import crontab
from datetime import datetime, timedelta
from tools.mailer import send_email
from flask import render_template

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # sender.add_periodic_task(crontab(hour = 10, minute= 00), send_daily_email.s(), name="Send email every 10 seconds")
    sender.add_periodic_task(20, monthly_report.s(), name="Send email every 20 seconds")

@celery.task
def sendHi(userid):
    user = User.query.filter_by(id=userid).first()
    return "Hi " + user.username

@celery.task
def add():
    return 3+4

# Daily reminders to the ones who have not logged in the last 24 hours
@celery.task
def send_daily_email():
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    inactive_users = User.query.filter(User.lastLoggedIn < twenty_four_hours_ago).filter(User.role == "user").all()
    message = "Hey you are getting this email because you haven't logged in in the last 24 hours"
    count = 0 
    for user in inactive_users:
        count += 1
        html = render_template("daily_email.html", user=user, message=message)
        send_email(user.email, "Inactive User", html)
    return f"Reminder sent to {count} inactive users"

@celery.task
def monthly_report():
    users = User.query.filter_by(role="user").all()
    one_month_ago = datetime.now() - timedelta(days=30)

    for user in users:
        user_orders = Order.query.filter_by(user_id=user.id).filter(Order.order_date > one_month_ago).all()
        order_details = []
        total_amount_spent = 0

        for order in user_orders:
            order_details.append({
                "order_date": order.order_date,
                "product_names": [item.product.name for item in order.order_items],
                "total_order_value": order.total_amount
            })

            total_amount_spent += order.total_amount
        
        html = render_template("monthly_report.html", user=user, order_details=order_details, total_amount_spent=total_amount_spent)
        send_email(user.email, "Monthly Report", html)
    return f"Monthly report sent to {len(users)} users"