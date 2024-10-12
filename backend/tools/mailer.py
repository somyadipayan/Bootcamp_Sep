from flask_mail import Message, Mail
from flask import current_app as app

mail = Mail()

def init_app(app):
    mail.init_app(app)

def send_email(to, subject, body):
    
    sender = "noreply@store.com"
    msg = Message(subject, sender=sender, recipients=[to], html=body)

    mail.send(msg)


