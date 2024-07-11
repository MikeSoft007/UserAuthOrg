# from dotenv import load_dotenv
# import os

# load_dotenv()  # Load environment variables from .env file

# from app import create_app, db
# from config import config

# config_name = os.getenv('FLASK_CONFIG', 'default')
# app = create_app(config_name)

# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run()


from dotenv import load_dotenv
import os
from flask_migrate import Migrate
from app import create_app, db

load_dotenv()  # Load environment variables from .env file

config_name = os.getenv('FLASK_CONFIG', 'default')
app = create_app(config_name)
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()