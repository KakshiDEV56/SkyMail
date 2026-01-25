from dotenv import load_dotenv
import os

load_dotenv()

# ======================== SERVER CONFIGURATION ========================
SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_PORT = int(os.getenv("SERVER_PORT"))
SERVER_URL = os.getenv("SERVER_URL")
FRONTEND_URL = os.getenv("FRONTEND_URL")

# ======================== SECRET KEYS ========================
EMAIL_CONFIRMATION_SECRET_KEY = os.getenv("EMAIL_CONFIRMATION_SECRET_KEY")
PASSWORD_RESET_SECRET_KEY = os.getenv("PASSWORD_RESET_SECRET_KEY")
ACCESS_TOKEN_SECRET_KEY = os.getenv("ACCESS_TOKEN_SECRET_KEY")

# ======================== GOOGLE OAUTH CONFIGURATION ========================
GOOGLE_OAUTH_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_OAUTH_SECRET_KEY = os.getenv("GOOGLE_OAUTH_SECRET_KEY") 
GOOGLE_OAUTH_SESSION_KEY = os.getenv("GOOGLE_OAUTH_SESSION_KEY")

# ======================== TOKEN EXPIRATION CONFIGURATION ========================
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
RESET_TOKEN_EXPIRE_MINUTES = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES", 15))
CONFIRMATION_ACCOUNT_TOKEN_EXPIRE_MINUTES = float(os.getenv("CONFIRMATION_ACCOUNT_TOKEN_EXPIRE_MINUTES", 2))

# ======================== DATABASE CONFIGURATION ========================
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST', 'localhost')}:5432/"
    f"{os.getenv('DB_NAME')}"
) 

# ======================== REDIS CONFIGURATION ========================
REDIS_URL = os.getenv("REDIS_URL")

# ======================== MAIL SERVER CONFIGURATION ========================
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_SMTP_HOST = os.getenv("MAIL_SMTP_HOST", "smtp.gmail.com")
MAIL_SMTP_PORT = int(os.getenv("MAIL_SMTP_PORT", 587))

# ======================== RATE LIMITING CONFIGURATION ========================
LOGIN_RATE_LIMIT_PERIOD = int(os.getenv("LOGIN_RATE_LIMIT_PERIOD", 60))
PASSWORD_RATE_LIMIT_PERIOD = int(os.getenv("PASSWORD_RATE_LIMIT_PERIOD", 300))

# ======================== RAZORPAY CONFIGURATION ========================
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_SECRET_KEY = os.getenv("RAZORPAY_SECRET_KEY")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")

# ======================== AWS S3 CONFIGURATION ========================
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_S3_REGION = os.getenv("AWS_S3_REGION", "us-east-1") 