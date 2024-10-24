from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.message import EmailMessage

def sendClientGmail(data, creds, client_email):

  # Authorize Gmail API
  service = build("gmail", "v1", credentials=creds)

  # Create email
  message = EmailMessage()

  message.set_content(data)

  message["To"] = client_email
  message["From"] = "aa@agmtechnology.com"
  message["Subject"] = "Confirmacion Compra"

  encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
  create_message = {"raw": encoded_message}

  # Send message
  send_message = (
      service.users()
      .messages()
      .send(userId="me", body=create_message)
      .execute()
  )

  print(f'Email sent: {send_message["id"]}')