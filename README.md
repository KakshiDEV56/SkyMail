# SkyMail - Newsletter & Campaign Platform

A FastAPI-based platform for managing newsletters, subscriber lists, and email campaigns. Includes scheduled sending, subscriber management, template builder, and payment integration.

## Setup

### Requirements
- Python 3.12+
- PostgreSQL 12+
- Redis 6+

### Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   ```
   Update `.env` with your database, AWS, and payment credentials.

3. **Set up database:**
   ```bash
   alembic upgrade head
   ```

4. **Start services:**
   ```bash
   # Terminal 1: Redis
   redis-server
   
   # Terminal 2: Celery worker
   celery -A app.celery_app worker --loglevel=info
   
   # Terminal 3: Celery beat (scheduler)
   celery -A app.celery_app beat --loglevel=info
   
   # Terminal 4: API server
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## Project Structure

```
app/
├── config/              # Configuration files
├── database/            # Database models and setup
├── middlewares/         # Custom middleware
├── modules/             # Feature modules
│   ├── auth/           # Authentication & company management
│   ├── billing/        # Payment & subscriptions
│   ├── campaign/       # Email campaigns
│   ├── newsletters/    # Templates & assets
│   └── subscribers/    # Subscriber management
├── utils/              # Helpers (constants, JWT, passwords)
├── workers/            # Celery tasks (email sending, scheduling)
├── redis/              # Redis client
└── main.py             # FastAPI app entry point
```

## Key Features

- **Authentication:** Email/password login, JWT tokens, refresh tokens
- **Companies:** Multi-tenant support with role-based access
- **Subscribers:** Manage email lists, subscribe/unsubscribe
- **Templates:** Create HTML email templates with variables
- **Campaigns:** Schedule campaigns, send to subscriber lists
- **Variables:** System variables (company_name, subscriber_email) + custom constants
- **Assets:** Upload images/assets to S3 for template use
- **Email Sending:** AWS SES integration with Celery task queue
- **Payments:** Razorpay integration for premium plans

## API Endpoints

Main routes are organized by module:
- `/api/auth/` - Authentication & company profile
- `/api/campaigns/` - Campaign CRUD and management
- `/api/newsletters/templates/` - Email templates
- `/api/subscribers/` - Subscriber lists
- `/api/billing/` - Payment information

Run the server and visit `/docs` for full API documentation (Swagger UI).

## Environment Variables

See `.env.example` for all available settings. Key ones:

- `DB_*` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `MAIL_USERNAME/PASSWORD` - AWS SES credentials (NOT S3 keys)
- `AWS_ACCESS_KEY_ID/SECRET` - S3 bucket access
- `RAZORPAY_*` - Payment gateway

## Database Migrations

Add new migrations after schema changes:
```bash
alembic revision --autogenerate -m "description of change"
alembic upgrade head
```

## Troubleshooting

**Emails not sending:**
- Check AWS SES credentials (separate from S3 keys)
- Verify sender email is verified in AWS SES
- Check Celery worker is running

**Template variable errors:**
- System variables (company_name, subscriber_email, etc.) are auto-filled
- Custom variables must be defined in campaign constants
- template_asset contains comma-separated URLs of uploaded files

**Database connection issues:**
- Ensure PostgreSQL is running
- Check DB_HOST, DB_USER, DB_PASSWORD in .env
- Run `alembic upgrade head` to initialize schema

## Testing

```bash
# Run tests (if available)
pytest tests/
```

## Deployment Notes

- Change all SECRET_KEY values in production
- Use strong DB passwords
- Enable HTTPS for FRONTEND_URL
- Configure proper AWS S3 bucket policies
- Set ENV=production
- Use strong Razorpay API keys
