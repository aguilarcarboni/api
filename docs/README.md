# LaserFocus API Documentation

## Overview
This document describes the API schema for the laserfocus application. The API provides endpoints for drive operations, database operations, and wallet functionality.

## General Response Format
All endpoints follow a standard response format:
```json
{
"status": "success" | "error",
"content": { any }
}
```

## Endpoints

### Drive Operations
Description: The drive endpoints handle file and folder operations.
1. **Query Files**
   - Path: `/drive/query_files`
   - Method: POST
   - Request: `{ "path": "string" }`

2. **Query File**
   - Path: `/drive/query_file`
   - Method: POST
   - Request: `{ "path": "string", "file_name": "string" }`

3. **Download File**
   - Path: `/drive/download_file`
   - Method: POST
   - Request: `{ "file_name": "string" }`

4. **Upload File**
   - Path: `/drive/upload_file`
   - Method: POST
   - Request: `{ "file": "binary", "parent_folder_id": "string" }`

5. **Delete File**
   - Path: `/drive/delete_file`
   - Method: POST
   - Request: `{ "file_ids": ["string"] }`

6. **Create Folder**
   - Path: `/drive/create_folder`
   - Method: POST
   - Request: `{ "folder_name": "string", "parent_folder_id": "string" }`

### Database Operations
Description: The database endpoints provide CRUD operations and additional queries for database management.

1. **Create**
   - Path: `/database/create`
   - Method: POST
   - Request: `{ "table": "string", "data": {} }`

2. **Read**
   - Path: `/database/read`
   - Method: POST
   - Request: `{ "table": "string", "params": {} }`

3. **Update**
   - Path: `/database/update`
   - Method: POST
   - Request: `{ "table": "string", "params": {}, "data": {} }`

4. **Delete**
   - Path: `/database/delete`
   - Method: POST
   - Request: `{ "table": "string", "params": {} }`

5. **Get Foreign Keys**
   - Path: `/database/get_foreign_keys`
   - Method: POST
   - Request: `{ "table": "string", "params": {} }`

6. **Get Parent Lineage**
   - Path: `/database/get_parent_lineage`
   - Method: POST
   - Request: `{ "table": "string", "params": {}, "depth": integer }`
   - Note: Depth is optional, default is 3, min is 1, max is 10

## Notes for LLMs
- Always refer to the specific endpoint documentation for required fields and data types