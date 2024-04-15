import sys

sys.path.append('src')
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Environment, FileSystemLoader
import os
from dotenv import load_dotenv
from errorHandling.errorHandlerWrapper import asyncWrapper
import asyncio

load_dotenv()


async def sentAccountVerificarionMail(email, userId, userName):
    verificationLink = "https://vehinav.onrender.com/account/verify/?userId="+userId
    env = Environment(loader=FileSystemLoader('src/templates'))
    template = env.get_template("account-verification.html")
    html_content = template.render(
        verification_link=verificationLink,
        userName=userName
    )
    # VHTML=render_template('account-verification.html',verification_link=verificationLink)
    server = smtplib.SMTP(os.environ.get('smtp_server_name'), int(os.environ.get('smtp_server_port')))
    server.starttls()
    server.login(os.environ.get('smtp_gmail_username'), os.environ.get('smtp_gmail_pass'))

    msg = MIMEMultipart()
    msg [ 'From' ] = os.environ.get('smtp_gmail_username')
    msg [ 'To' ] = email
    msg [ 'Subject' ] = "Account Verification | Trace Track"

    msg.attach(MIMEText(html_content, 'html'))

    server.sendmail(os.environ.get('smtp_gmail_username'), email, msg.as_string())
    server.quit()
    return True
# asyncio.run(sentAccountVerificarionMail("sameershaik2406@gmail.com",'4ba6f90f-ac3f-4e40-906f-4d57a1159e26','sameer'))
