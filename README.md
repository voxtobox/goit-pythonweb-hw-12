# goit-pythonweb-hw-10

An asynchronous web application built with FastAPI, featuring PostgreSQL integration, JWT-based authentication, email
support, and Cloudinary image uploads.

## 🚀 Technologies Used

- **FastAPI**
- **PostgreSQL** with `asyncpg`
- **SQLAlchemy** + **Alembic**
- **Pydantic v2**
- **JWT** (via `python-jose`)
- **FastAPI-Mail**
- **Cloudinary**
- **Rate limiting** with `slowapi`
- **Docker + Poetry**

## ⚙️ Setup

1. Copy `.env.example` to `.env` and fill in your configuration:

```bash
cp .env.example .env
```

2. Build and run the application:

```bash
docker compose up --build
```

3. The app will be available at:

```
http://localhost:8000
```

## 🛠️ Database Migrations

To apply Alembic migrations inside the running container:

```bash
docker exec -it python_app alembic upgrade head
```

## ✉️ Email Configuration

The app uses **FastAPI-Mail**. Be sure to provide correct SMTP credentials in the `.env` file.