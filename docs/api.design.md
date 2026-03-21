# DevCollab API Design

## Base URL
/api/v1

## Authentication
All endpoints except /auth/register and /auth/login require:
Header: Authorization: Bearer <token>

## Users
| Method | Endpoint | Description | Status Codes |
|--------|----------|-------------|--------------|
| GET | /users | Get all users | 200 |
| GET | /users/{username} | Get one user | 200, 404 |
| POST | /users | Create user | 201, 409 |
| PATCH | /users/{username} | Update user | 200, 404 |
| DELETE | /users/{username} | Deactivate user | 204, 404 |

## Projects
| Method | Endpoint | Description | Status Codes |
|--------|----------|-------------|--------------|
| GET | /projects | Get all projects | 200 |
| POST | /projects | Create project | 201 |
| GET | /projects/{id} | Get one project | 200, 404 |
| PATCH | /projects/{id} | Update project | 200, 404 |
| DELETE | /projects/{id} | Delete project | 204, 404 |

## Tasks
| Method | Endpoint | Description | Status Codes |
|--------|----------|-------------|--------------|
| GET | /projects/{id}/tasks | Get all tasks | 200 |
| POST | /projects/{id}/tasks | Create task | 201 |
| PATCH | /projects/{id}/tasks/{task_id} | Update task | 200, 404 |
| DELETE | /projects/{id}/tasks/{task_id} | Delete task | 204, 404 |

## Error Response Format
All errors return this shape:
{
    "error": "short_error_code",
    "message": "Human readable message",
    "details": {}
}

## Success Response Format
All successful responses return this shape:
{
    "data": {},
    "message": "Success"
}