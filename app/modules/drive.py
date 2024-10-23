from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload, MediaIoBaseUpload
import os
import io

from app.helpers.response import Response
from app.helpers.logger import logger

SCOPES = ['https://www.googleapis.com/auth/drive']

import os
from dotenv import load_dotenv

load_dotenv()

logger.info('Initializing Google Drive')
creds = Credentials(
    token=os.getenv('GOOGLE_TOKEN'),
    refresh_token=os.getenv('GOOGLE_REFRESH_TOKEN'),
    token_uri=os.getenv('GOOGLE_TOKEN_URI'),
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    scopes=SCOPES
)
service = build("drive", "v3", credentials=creds)
logger.success('Successfully initialized Google Drive')

def createFolder(folderName, parentFolderId):

    logger.info(f"Creating folder: {folderName} in folder: {parentFolderId}")

    fileMetadata = {
        'name': folderName,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parentFolderId is not None:
        fileMetadata['parents'] = [parentFolderId]
    else:
        logger.error("No parent folder ID provided.")
        return Response.error('No parent folder ID provided.')
    
    folder = service.files().create(body=fileMetadata, fields='id, name, parents, mimeType, size, modifiedTime, createdTime').execute()
    logger.success(f"Successfully created folder: {folderName} in folder: {parentFolderId}")
    return Response.success(folder)

# Upload folder

# Upload files

def uploadFileWithPath(filePath, parentFolderId):
    logger.info(f"Uploading file: {filePath} to folder: {parentFolderId}")
    fileMetadata = {'name': os.path.basename(filePath)}

    if parentFolderId is not None:
        fileMetadata['parents'] = [parentFolderId]
    else:
        logger.error("No parent folder ID provided.")
        return Response.error('No parent folder ID provided.')
    
    media = MediaFileUpload(filePath, resumable=True)
    f = service.files().create(body=fileMetadata, media_body=media, fields='id, name, parents, mimeType, size, modifiedTime').execute()
    print(f)
    logger.success(f"Successfully uploaded file: {filePath} to folder: {parentFolderId}")
    return Response.success(f)

def uploadFile(fileName, rawFile, parentFolderId):
    logger.info(f"Uploading file: {fileName} to folder: {parentFolderId}")
    fileMetadata = {'name': fileName}

    if parentFolderId is not None:
        fileMetadata['parents'] = [parentFolderId]
    else:
        logger.error("No parent folder ID provided.")
        return Response.error('No parent folder ID provided.')
    print(f)
    try:
        media = MediaIoBaseUpload(rawFile, resumable=True)
        f = service.files().create(body=fileMetadata, media_body=media, fields='id, name, parents, mimeType, size, modifiedTime').execute()
        logger.success(f"Successfully uploaded file: {fileName} to folder: {parentFolderId}")
        return Response.success(f)
    except Exception as e:
        logger.error(f"Error uploading file: {fileName}. Error: {str(e)}")
        return Response.error(f'Error uploading file: {str(e)}')

# Modify files?

def deleteFiles(file_ids):

    logger.info(f"Deleting files with IDs: {file_ids}")

    results = []
    for file_id in file_ids:
        try:
            response = service.files().delete(fileId=file_id).execute()
            logger.success(f"Successfully deleted file with ID: {file_id}")
            results.append(Response.success({'content': response, 'file_id': file_id}))
        except Exception as e:
            logger.error(f"Error deleting file with ID: {file_id}. Error: {str(e)}")
            results.append(Response.error({'content': f'Error deleting file: {str(e)}', 'file_id': file_id}))

    logger.success(f"Deletion process completed for {len(file_ids)} files.")
    return results  



def queryFile(path, file_name):

    logger.info(f"Querying for file: {path}/{file_name}")

    path = path + '/' + file_name
    paths = path.split('/')

    parentId = 'root'
    files = []

    for index, path in enumerate(paths):
        print(path, file_name)
        try:

                response = (
                    service.files()
                    .list(
                        q=f"name='{path}' and trashed = false and '{parentId}' in parents",
                        spaces="drive",
                        fields="files(id, name, mimeType, size, modifiedTime, parents)",
                    )
                    .execute()
                )
                
                filesResponse = response.get("files")
                print(filesResponse)
                logger.info(f'Current path: {filesResponse[0]["name"]}')
                files.append(filesResponse[0])
                parentId = files[index]['id']

        except HttpError as error:
            logger.error(f"An error occurred. {error}")
            return Response.error(error)
        
        except:
            logger.error("Error querying file.")
            return Response.error('Error querying file.')
    
    logger.success(f"Successfully queried file: {files[len(files) - 1]}")
    return Response.success(files[len(files) - 1])

def queryFilesInFolder(path):

    logger.info(f"Querying for files in: {path}")

    path = path + '/'
    paths = path.split('/')

    parentID = 'root'

    for index, currentPath in enumerate(paths):

        query = f"trashed = false and '{parentID}' in parents"

        if index < len(paths) - 1:
            query =f"name='{currentPath}' and trashed = false and '{parentID}' in parents"

        if path == '/':
            query =f"trashed = false and 'root' in parents"

        try:

                response = (
                    service.files()
                    .list(
                        q=query,
                        spaces="drive",
                        fields="files(id, name, mimeType, size, modifiedTime, parents)",
                    )
                    .execute()
                )

                parentID = response['files'][0]['id']

        except HttpError as error:
            logger.error(f"An error occurred. {error}")
            return Response.error(error)
    
        except:
            logger.error("Error querying files.")
            return Response.error('Error querying files.')
    
    logger.success(f"Successfully queried files in: {paths[len(paths) - 1]}")
    return Response.success(response)



def downloadFile(fileId):

    logger.info(f"Downloading file with ID: {fileId}")

    try:
        request = service.files().get_media(fileId=fileId)
        downloaded_file = io.BytesIO()
        downloader = MediaIoBaseDownload(downloaded_file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logger.info(f"Download {int(status.progress() * 100)}.")

    except HttpError as error:
        logger.error(f"An error occurred: {error}")
        return Response.error(error)
    
    except:
        logger.error("Error downloading file.")
        return Response.error('Error downloading file.')
    
    logger.success("Successfully downloaded file.")
    return Response.success(downloaded_file.getvalue())


# Download zip?