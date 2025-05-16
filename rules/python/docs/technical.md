# Python Project Technical Specifications

## Overview

This document outlines the technical architecture and patterns for our Python project. The system follows a layered architecture with clear separation of concerns.

## Technology Stack

- **Language**: Python 3.10+
- **Web Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL
- **Task Queue**: Celery with Redis
- **Testing**: pytest
- **Documentation**: Sphinx
- **Containerization**: Docker

## Core Architecture

### Layered Architecture

```python
# src/api/endpoint.py - API Layer Example
from fastapi import APIRouter, Depends
from src.services.user_service import UserService
from src.api.dto.user_dto import UserCreateDTO, UserResponseDTO

router = APIRouter()

@router.post("/users", response_model=UserResponseDTO)
async def create_user(
    user_data: UserCreateDTO,
    user_service: UserService = Depends()
):
    return await user_service.create_user(user_data)
```

```python
# src/services/user_service.py - Service Layer Example
from src.repositories.user_repository import UserRepository
from src.domain.models.user import User
from src.api.dto.user_dto import UserCreateDTO

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        
    async def create_user(self, user_data: UserCreateDTO) -> User:
        # Business logic
        user = User(
            email=user_data.email,
            username=user_data.username
        )
        return await self.user_repository.create(user)
```

```python
# src/repositories/user_repository.py - Repository Layer Example
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models.user import User

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
```

## Dependency Injection

We use FastAPI's dependency injection system:

```python
# src/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_session
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService

def get_user_repository(session: AsyncSession = Depends(get_session)) -> UserRepository:
    return UserRepository(session)

def get_user_service(
    repository: UserRepository = Depends(get_user_repository)
) -> UserService:
    return UserService(repository)
```

## Error Handling

All exceptions should be handled properly:

```python
# src/exceptions.py
from fastapi import HTTPException, status

class NotFoundError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class ValidationError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )
```

## Testing Strategy

We follow a pyramid testing approach:

1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test interactions between components
3. **End-to-End Tests**: Test the entire system flow

Example test:

```python
# tests/services/test_user_service.py
import pytest
from src.services.user_service import UserService
from src.repositories.user_repository import UserRepository
from src.api.dto.user_dto import UserCreateDTO

@pytest.fixture
def user_repository_mock():
    return Mock(spec=UserRepository)

@pytest.fixture
def user_service(user_repository_mock):
    return UserService(user_repository_mock)

async def test_create_user(user_service, user_repository_mock):
    # Arrange
    user_dto = UserCreateDTO(email="test@example.com", username="testuser")
    user_repository_mock.create.return_value = User(id=1, email="test@example.com", username="testuser")
    
    # Act
    result = await user_service.create_user(user_dto)
    
    # Assert
    assert result.id == 1
    assert result.email == "test@example.com"
    assert result.username == "testuser"
    user_repository_mock.create.assert_called_once()
```

## Background Tasks

For long-running operations, we use Celery tasks:

```python
# src/tasks/email_tasks.py
from celery import shared_task
from src.services.email_service import EmailService

@shared_task
def send_welcome_email(user_id: int):
    email_service = EmailService()
    email_service.send_welcome_email(user_id)
```

## Logging

We follow a structured logging approach:

```python
# src/logging.py
import logging
import json
from datetime import datetime

class CustomJSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if hasattr(record, "extra"):
            log_record.update(record.extra)
        return json.dumps(log_record)
```

## Authentication

We use JWT for authentication:

```python
# src/auth/jwt.py
from datetime import datetime, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

## Deployment

We use Docker for containerization:

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Performance Considerations

1. Use async/await for I/O-bound operations
2. Implement caching for frequently accessed data
3. Use connection pooling for database connections
4. Optimize database queries with proper indexing
5. Use pagination for large data sets

## Security Guidelines

1. Validate all user inputs
2. Use parameterized queries to prevent SQL injection
3. Sanitize all outputs to prevent XSS
4. Use HTTPS for all communications
5. Implement rate limiting for API endpoints
6. Regularly update dependencies
7. Follow the principle of least privilege 