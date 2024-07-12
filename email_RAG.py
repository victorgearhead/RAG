from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import getpass
import imaplib
import email
import smtplib
import time
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from pymongo import MongoClient

def send_email(sender_email,sender_password,recipient_email,subject,message,attachment):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    if attachment:
        attachment_part = MIMEBase('application', 'octet-stream')
        with open(attachment, 'rb') as attachment_file:
            attachment_part.set_payload(attachment_file.read())
        encoders.encode_base64(attachment_part)
        attachment_part.add_header('Content-Disposition', f'attachment; filename= {attachment}')
        msg.attach(attachment_part)

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

    print("Mail sent successfully")
    time.sleep(3)

def send_mail():
    sender_email = input('Enter your email: ')
    sender_password = getpass.getpass('Enter your password(APP PASSWORD(Google Authetication)): ')
    recipient_email = input('Enter recipient email address: ')
    subject = input('Enter email subject: ')
    message = input('Enter email message: ')
    attachment = input('Enter attachment file path (press Enter if none): ')

    send_email(sender_email,sender_password,recipient_email,subject,message,attachment)


def fetch_emails(email_address, password):

    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(email_address, password)
    mail.select('inbox')

    engine = create_engine('sqlite:///email_database.db', echo=True)
    Base = declarative_base()

    class Email(Base):
        __tablename__ = 'emails'
        id = Column(Integer, primary_key=True)
        sender = Column(String)
        subject = Column(String)
        body = Column(Text)

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    _, data = mail.search(None, 'UNSEEN')
    email_ids = data[0].split()[::-1]

    for email_id in email_ids:
         
        _, data = mail.fetch(email_id, '(RFC822)')
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        sender = msg['From']
        subject = msg['Subject']
        body = msg.get_payload()

        print('From:', sender)
        print('Subject:', subject)
        print('Body:', body)
        print('Data is being RAGed, Delete "email_database.db". ')

        email_entry = Email(sender=sender, subject=subject, body=body)
        session.add(email_entry)
        
    session.commit()

    mail.logout()
    session.close()
    print("DONE")
    time.sleep(3)

def mail_view():
    email_address = input('Enter your email: ')
    password = getpass.getpass('Enter your password(APP PASSWORD(Google Authetication)): ')

    fetch_emails(email_address, password)

