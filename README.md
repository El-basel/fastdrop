# FastDrop

A secure, modern file sharing application built with FastAPI. Upload files, share them via unique links, and manage your uploads with optional user authentication.

## Features

### Anonymous Users
- **Quick file uploads** - No account required
- **Shareable links** - Get instant download links for your files
- **Automatic expiration** - Files auto-delete after 7 days
- **Secure deletion** - JWT-based deletion tokens for removing files

### Authenticated Users
- **Extended storage** - Files persist for 90 days
- **Upload management** - View and manage all your uploads in one place
- **Account dashboard** - Track download counts and file status
- **Easy file control** - Delete or deactivate links anytime

### Security
- **JWT-based authentication** - Secure token-based auth system
- **Password hashing** - Argon2 password protection
- **Timing attack prevention** - Constant-time comparison for login
- **Secure deletion tokens** - Signed, expiring tokens for file deletion

## Tech Stack

- **FastAPI** - Modern, high-performance web framework
- **SQLModel** - SQL databases with Python type annotations
- **Pydantic** - Data validation using Python type hints
- **JWT** - Secure token generation and validation
- **pwdlib** - Password hashing
- **PostgreSQL** - Database

## Project Structure
```
fastdrop/
├── main.py              # Application entry point
├── config.py            # Environment variables and configuration
├── dependencies.py      # FastAPI dependencies and OAuth2 setup
├── models.py            # SQLModel database models
├── utils.py             # Helper functions
├── routers/
│   ├── files.py        # File upload/download/delete endpoints
│   └── auth.py         # User registration and login
```

## API Endpoints

### Files
- `POST /files` - Upload a file (authentication optional)
- `GET /files/{file_id}` - Download a file
- `DELETE /files/{file_id}` - Delete a file (requires deletion token or ownership)

### Authentication
- `POST /auth/register` - Create a new user account
- `POST /auth/login` - Login and receive access token

## Current Status

**Completed:**
- ✅ File upload/download/delete functionality
- ✅ Anonymous and authenticated upload support
- ✅ User registration and login
- ✅ JWT-based authentication
- ✅ Secure deletion tokens
- ✅ File expiration logic
- ✅ Organized file storage (year/month directories)

**In Progress:**
- 🚧 User dashboard (view uploaded files)
- 🚧 Frontend UI (HTMX + Alpine.js + Tailwind)
- 🚧 Admin panel (user management)

**Planned:**
- 📋 Virus scanning (VirusTotal API integration)
- 📋 Download analytics (track downloads, geographic data)
- 📋 File preview (images, PDFs)
- 📋 Email notifications
