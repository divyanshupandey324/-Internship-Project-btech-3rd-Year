


import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key")
    SQLALCHEMY_DATABASE_URI = (
    "mysql+pymysql://ufquegmkfvzxgklh:di57GgsCPzk0iVOcCDuI@butxnm9ctrz7w0z06p2a-mysql.services.clever-cloud.com:3306/butxnm9ctrz7w0z06p2a"
    )


    UPLOAD_FOLDER = "static/uploads"
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
