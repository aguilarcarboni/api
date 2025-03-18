# API Endpoints Documentation

This document provides a comprehensive overview of all available API endpoints in the application.

## Project Endpoints

All project endpoints use POST method and expect a JSON payload.

- `POST /create`
  - Creates a new project
  - Payload: `{ "data": { ... } }`

- `POST /read`
  - Retrieves project(s) based on parameters
  - Payload: `{ "params": { ... } }`

- `POST /update`
  - Updates existing project(s)
  - Payload: `{ "params": { ... }, "data": { ... } }`

- `POST /delete`
  - Deletes project(s)
  - Payload: `{ "params": { ... } }`

## Event Endpoints

All event endpoints use POST method and expect a JSON payload.

- `POST /create`
  - Creates a new event
  - Payload: `{ "data": { ... } }`

- `POST /read`
  - Retrieves event(s) based on parameters
  - Payload: `{ "params": { ... } }`

- `POST /update`
  - Updates existing event(s)
  - Payload: `{ "params": { ... }, "data": { ... } }`

- `POST /delete`
  - Deletes event(s)
  - Payload: `{ "params": { ... } }`

## Document Center Endpoints

- `GET /folder_dictionary`
  - Retrieves the folder structure dictionary
  - No payload required

- `POST /read`
  - Reads files based on parameters
  - Payload: `{ "params": { ... } }`

- `POST /delete`
  - Deletes a document
  - Payload: `{ "document": { ... }, "parent_folder_id": "..." }`

- `POST /upload`
  - Uploads a new file
  - Payload: `{
    "file_name": "...",
    "mime_type": "...",
    "file_data": "...",
    "parent_folder_id": "...",
    "document_info": { ... },
    "uploader": "..."
  }`

## Email Endpoints

- `POST /send_email`
  - Sends an email using Gmail
  - Payload: `{
    "content": "...",
    "client_email": "...",
    "subject": "...",
    "email_template": "..."
  }`

## User Endpoints

All user endpoints use POST method and expect a JSON payload.

- `POST /create`
  - Creates a new user
  - Payload: `{ "data": { ... } }`

- `POST /read`
  - Retrieves user(s) based on parameters
  - Payload: `{ "params": { ... } }`

- `POST /update`
  - Updates existing user(s)
  - Payload: `{ "params": { ... }, "data": { ... } }`

- `POST /delete`
  - Deletes user(s)
  - Payload: `{ "params": { ... } }`

## Space Endpoints

All space endpoints use POST method and expect a JSON payload.

- `POST /create`
  - Creates a new space
  - Payload: `{ "data": { ... } }`

- `POST /read`
  - Retrieves space(s) based on parameters
  - Payload: `{ "params": { ... } }`

- `POST /update`
  - Updates existing space(s)
  - Payload: `{ "params": { ... }, "data": { ... } }`

- `POST /delete`
  - Deletes space(s)
  - Payload: `{ "params": { ... } }`

## Task Endpoints

All task endpoints use POST method and expect a JSON payload.

- `POST /create`
  - Creates a new task
  - Payload: `{ "data": { ... } }`

- `POST /read`
  - Retrieves task(s) based on parameters
  - Payload: `{ "params": { ... } }`

- `POST /update`
  - Updates existing task(s)
  - Payload: `{ "params": { ... }, "data": { ... } }`

- `POST /delete`
  - Deletes task(s)
  - Payload: `{ "params": { ... } }`

- `POST /create-link`
  - Creates a link between tasks
  - Payload: `{ "data": { ... } }`

- `POST /read-links`
  - Retrieves task links based on parameters
  - Payload: `{ "params": { ... } }` 