import os

class Config:
    # Use an environment variable for the database URI
    # Clever Cloud will provide this. You'll set it as an environment variable in Render.
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://username:password@localhost/dbname"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
