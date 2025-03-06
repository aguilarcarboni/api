import os
import base64
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional, Union

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

  def send_email(self, plain_text: str, to_email: str, subject: str) -> Response:
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

  def create_draft(self, plain_text: str, to_email: str, subject: str) -> Response:
    """Create a draft email."""
    try:
        message = MIMEMultipart('related')
        message['To'] = to_email
        message['Subject'] = subject
        message.attach(MIMEText(plain_text, 'plain'))
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        draft = {'message': {'raw': raw_message}}
        
        draft = self.service.users().drafts().create(userId="me", body=draft).execute()
        logger.success(f'Successfully created draft')
        return Response.success({'draftId': draft['id']})
    except Exception as e:
        return Response.error(f"Error creating draft: {str(e)}")

  def list_messages(self, query: str = None, max_results: int = 10) -> Response:
    """List messages matching the specified query."""
    try:
        logger.info(f'Listing messages with query: {query} and max results: {max_results}')
        messages = []
        request = self.service.users().messages().list(
            userId="me", q=query, maxResults=max_results
        )
        
        while request and len(messages) < max_results:
            response = request.execute()
            messages.extend(response.get('messages', []))
            request = self.service.users().messages().list_next(request, response)
        
        detailed_messages = []
        for msg in messages[:max_results]:
            message = self.service.users().messages().get(
                userId="me", id=msg['id'], format='metadata'
            ).execute()
            headers = {header['name']: header['value'] for header in message['payload']['headers']}
            detailed_messages.append({
                'id': message['id'],
                'threadId': message['threadId'],
                'subject': headers.get('Subject', ''),
                'from': headers.get('From', ''),
                'date': headers.get('Date', ''),
                'snippet': message.get('snippet', '')
            })
        
        logger.success(f'Successfully listed messages')
        return Response.success({'messages': detailed_messages})
    except Exception as e:
        logger.error(f"Error listing messages: {str(e)}")
        return Response.error(f"Error listing messages: {str(e)}")

  def get_message(self, message_id: str) -> Response:
    """Get a specific message's full details."""
    try:
        logger.info(f'Getting message with id: {message_id}')
        message = self.service.users().messages().get(
            userId="me", id=message_id, format='full'
        ).execute()
        
        headers = {header['name']: header['value'] for header in message['payload']['headers']}
        parts = self._get_message_parts(message['payload'])
        logger.success(f'Successfully got message')
        return Response.success({
            'id': message['id'],
            'threadId': message['threadId'],
            'subject': headers.get('Subject', ''),
            'from': headers.get('From', ''),
            'to': headers.get('To', ''),
            'date': headers.get('Date', ''),
            'body': parts,
            'labels': message['labelIds']
        })
    except Exception as e:
        logger.error(f"Error getting message: {str(e)}")
        return Response.error(f"Error getting message: {str(e)}")

  def _get_message_parts(self, payload: Dict) -> List[Dict]:
    """Helper method to recursively get all parts of a message."""
    parts = []
    
    if 'parts' in payload:
        for part in payload['parts']:
            parts.extend(self._get_message_parts(part))
    elif 'body' in payload and payload['body'].get('data'):
        parts.append({
            'mimeType': payload['mimeType'],
            'data': base64.urlsafe_b64decode(
                payload['body']['data'].encode('UTF-8')
            ).decode('utf-8')
        })
    
    return parts

  def modify_labels(self, message_id: str, add_labels: List[str] = None, remove_labels: List[str] = None) -> Response:
    """Modify the labels of a specific message."""
    try:
        logger.info(f'Modifying labels of message with id: {message_id}')
        body = {
            'addLabelIds': add_labels or [],
            'removeLabelIds': remove_labels or []
        }
        message = self.service.users().messages().modify(
            userId="me", id=message_id, body=body
        ).execute()
        logger.success(f'Successfully modified labels')
        return Response.success({'messageId': message['id'], 'labels': message['labelIds']})
    except Exception as e:
        logger.error(f"Error modifying labels: {str(e)}")
        return Response.error(f"Error modifying labels: {str(e)}")

  def list_threads(self, query: str = None, max_results: int = 10) -> Response:
    """List email threads matching the specified query."""
    try:
        logger.info(f'Listing threads with query: {query} and max results: {max_results}')
        threads = []
        request = self.service.users().threads().list(
            userId="me", q=query, maxResults=max_results
        )
        
        while request and len(threads) < max_results:
            response = request.execute()
            threads.extend(response.get('threads', []))
            request = self.service.users().threads().list_next(request, response)
        
        detailed_threads = []
        for thread in threads[:max_results]:
            thread_data = self.service.users().threads().get(
                userId="me", id=thread['id']
            ).execute()
            
            messages = thread_data['messages']
            last_message = messages[-1]
            headers = {header['name']: header['value'] for header in last_message['payload']['headers']}
            
            detailed_threads.append({
                'id': thread_data['id'],
                'messageCount': len(messages),
                'subject': headers.get('Subject', ''),
                'lastFrom': headers.get('From', ''),
                'lastDate': headers.get('Date', ''),
                'snippet': last_message.get('snippet', '')
            })
        
        logger.success(f'Successfully listed threads')
        return Response.success({'threads': detailed_threads})
    except Exception as e:
        logger.error(f"Error listing threads: {str(e)}")
        return Response.error(f"Error listing threads: {str(e)}")

  def get_thread(self, thread_id: str) -> Response:
    """Get a complete thread with all messages."""
    try:
        logger.info(f'Getting thread with id: {thread_id}')
        thread = self.service.users().threads().get(userId="me", id=thread_id).execute()
        messages = []
            
        for message in thread['messages']:
            headers = {header['name']: header['value'] for header in message['payload']['headers']}
            parts = self._get_message_parts(message['payload'])
            
            messages.append({
                'id': message['id'],
                'subject': headers.get('Subject', ''),
                'from': headers.get('From', ''),
                'to': headers.get('To', ''),
                'date': headers.get('Date', ''),
                'body': parts,
                'labels': message['labelIds']
            })
        
        logger.success(f'Successfully got thread')
        return Response.success({
            'threadId': thread['id'],
            'messages': messages
        })
    except Exception as e:
        logger.error(f"Error getting thread: {str(e)}")
        return Response.error(f"Error getting thread: {str(e)}")

  def fetch_detailed_emails(self, query: str = None, max_results: int = 10) -> Response:
    """Fetch detailed emails with their threads in a single call."""
    try:
        logger.info(f'Fetching detailed emails with query: {query} and max results: {max_results}')
        threads = []
        request = self.service.users().threads().list(
            userId="me", q=query, maxResults=max_results
        )
        
        while request and len(threads) < max_results:
            response = request.execute()
            threads.extend(response.get('threads', []))
            request = self.service.users().threads().list_next(request, response)
        
        detailed_emails = []
        for thread in threads[:max_results]:
            thread_data = self.service.users().threads().get(
                userId="me", id=thread['id']
            ).execute()
            
            messages = thread_data['messages']
            last_message = messages[-1]
            headers = {header['name']: header['value'] for header in last_message['payload']['headers']}
            
            # Process all messages in the thread
            thread_messages = []
            for message in messages:
                msg_headers = {header['name']: header['value'] for header in message['payload']['headers']}
                parts = self._get_message_parts(message['payload'])
                thread_messages.append({
                    'id': message['id'],
                    'subject': msg_headers.get('Subject', ''),
                    'from': msg_headers.get('From', ''),
                    'to': msg_headers.get('To', ''),
                    'date': msg_headers.get('Date', ''),
                    'body': parts,
                    'labels': message.get('labelIds', [])
                })
            
            # Extract name and email from the From field
            from_field = headers.get('From', '')
            name = from_field.split('<')[0].strip()
            email_match = from_field.split('<')[1].rstrip('>') if '<' in from_field else from_field
            
            detailed_emails.append({
                'id': thread_data['id'],
                'threadId': thread_data['id'],
                'name': name,
                'email': email_match,
                'subject': headers.get('Subject', ''),
                'text': last_message.get('snippet', ''),
                'date': headers.get('Date', ''),
                'read': 'UNREAD' not in last_message.get('labelIds', []),
                'labels': last_message.get('labelIds', []),
                'messages': thread_messages
            })
        
        logger.success(f'Successfully fetched detailed emails')
        return Response.success({'emails': detailed_emails})
    except Exception as e:
        logger.error(f"Error fetching detailed emails: {str(e)}")
        return Response.error(f"Error fetching detailed emails: {str(e)}")