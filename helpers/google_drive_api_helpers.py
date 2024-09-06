from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
from email.message import EmailMessage
import gspread
import pandas as pd

# todo
def authenticateGoogleDrive():
    
    # Google Drive Authentication
    SCOPES = ["https://www.googleapis.com/auth/drive", "https://mail.google.com/"]
    flow = InstalledAppFlow.from_client_secrets_file("creds/GoogleAuthPython.json", SCOPES)
    creds = flow.run_local_server(port=0)
    
    return creds

def read_gs(worksheet_name, sheet_name, creds):

  gs = gspread.authorize(creds)
  worksheet = gs.open(worksheet_name)

  sheet = worksheet.worksheet(sheet_name)

  df_sheet = gsheet_to_df(sheet)

  return df_sheet, sheet

def gsheet_to_df(worksheet):
  sheet_data = worksheet.get_all_values()

  df_sheet = pd.DataFrame(sheet_data)

  df_sheet.columns = df_sheet.iloc[0]
  df_sheet = df_sheet.iloc[1:]

  return df_sheet

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