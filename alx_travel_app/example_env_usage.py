"""
Example of how to use environment variables in Django
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Example usage of environment variables
def example_env_usage():
    """
    Examples of how to read environment variables with different data types
    """
    
    # Reading string values
    chapa_secret_key = os.getenv("CHAPA_SECRET_KEY")
    chapa_public_key = os.getenv("CHAPA_PUBLIC_KEY")
    
    # Reading with default values
    debug_mode = os.getenv("DEBUG", "False").lower() == "true"
    
    # Reading integer values
    max_upload_size = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))
    
    # Reading boolean values
    enable_logging = os.getenv("ENABLE_LOGGING", "True").lower() == "true"
    
    # Reading list values (comma-separated)
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "").split(",") if os.getenv("ALLOWED_HOSTS") else []
    
    # Reading database configuration
    database_url = os.getenv("DATABASE_URL")
    database_name = os.getenv("DATABASE_NAME", "default_db")
    database_user = os.getenv("DATABASE_USER", "default_user")
    database_password = os.getenv("DATABASE_PASSWORD", "")
    database_host = os.getenv("DATABASE_HOST", "localhost")
    database_port = int(os.getenv("DATABASE_PORT", "5432"))
    
    print("Environment Variables:")
    print(f"CHAPA_SECRET_KEY: {chapa_secret_key}")
    print(f"CHAPA_PUBLIC_KEY: {chapa_public_key}")
    print(f"DEBUG: {debug_mode}")
    print(f"MAX_UPLOAD_SIZE: {max_upload_size}")
    print(f"ENABLE_LOGGING: {enable_logging}")
    print(f"ALLOWED_HOSTS: {allowed_hosts}")
    print(f"DATABASE_URL: {database_url}")
    print(f"DATABASE_NAME: {database_name}")
    print(f"DATABASE_USER: {database_user}")
    print(f"DATABASE_HOST: {database_host}")
    print(f"DATABASE_PORT: {database_port}")

if __name__ == "__main__":
    example_env_usage()
