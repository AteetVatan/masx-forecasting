"""Welcome to MASX AI application init"""
import os
from dotenv import load_dotenv



from processors.raw_process import RawProcess

load_dotenv()

def init_app():    
    RawProcess.run_all()

if __name__ == "__main__":
    # Load environment variables from .env file    
    init_app()
    
