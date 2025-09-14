import os

class Config:
    SECRET_KEY = "supersecretkey"  # change this for production
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")

    # ✅ MySQL connection string
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123123123@localhost/rental_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
