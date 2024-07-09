import os,datetime

#PostgresQL DB connection
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_jwt_secret_key')

    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(minutes=15)  # Set the token expiration time

class DevelopmentConfig(Config):
    DEBUG = True

#Test db
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


# class Config:
#     # General Configurations
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     SECRET_KEY = 'your_secret_key'

# class DevelopmentConfig(Config):
#     DEBUG = True
#     SQLALCHEMY_DATABASE_URI = 'your_dev_db_uri'

# class TestingConfig(Config):
#     TESTING = True
#     SQLALCHEMY_DATABASE_URI = 'your_test_db_uri'
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     DEBUG = True

# class ProductionConfig(Config):
#     SQLALCHEMY_DATABASE_URI = 'your_prod_db_uri'

# config = {
#     'development': DevelopmentConfig,
#     'testing': TestingConfig,
#     'production': ProductionConfig
# }
