import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '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')
    DATABASE_PATH = 'data/emails.db'