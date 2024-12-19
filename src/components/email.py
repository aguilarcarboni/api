import os
import base64
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.utils.logger import logger
from src.utils.response import Response

class Gmail:

  def __init__(self):
    logger.announcement('Initializing Email', type='info')
    SCOPES = ["https://mail.google.com/"]
    try:
      creds = Credentials(
        token=os.getenv('GOOGLE_TOKEN'),
        refresh_token=os.getenv('GOOGLE_REFRESH_TOKEN'),
        token_uri=os.getenv('GOOGLE_TOKEN_URI'),
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        scopes=SCOPES
      )
      self.service = build("gmail", "v1", credentials=creds)
      logger.announcement('Initialized Email', type='success')
    except Exception as e:
      logger.error(f"Error initializing Email: {str(e)}")

  def send_email(self, plain_text, to_email, subject):
    try:
        logger.info(f'Sending email to: {to_email}')

        message = MIMEMultipart('related')
        message['To'] = to_email
        message['Subject'] = subject
        message.attach(MIMEText(plain_text, 'plain'))
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": raw_message}

        send_message = (
            self.service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        logger.success(f'Successfully sent email to: {to_email}')
        return Response.success({'emailId': send_message["id"]})
    
    except Exception as e:
        return Response.error(f"Error sending email: {str(e)}")