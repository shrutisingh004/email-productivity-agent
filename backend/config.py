import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-api-key')

    DATABASE_PATH = 'data/emails.db'

