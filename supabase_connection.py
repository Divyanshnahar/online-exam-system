import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables from .env file
load_dotenv()

def create_connection():
    """
    Creates and returns a connection to Supabase.
    Returns None if connection fails.
    """
    try:
        # Get Supabase credentials from environment variables
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("Error: Supabase URL or key not found in environment variables")
            print("Make sure you have a .env file with SUPABASE_URL and SUPABASE_KEY")
            return None
            
        # Create Supabase client
        supabase = create_client(supabase_url, supabase_key)
        return supabase
    
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        return None

def test_connection():
    """
    Tests the Supabase connection by performing a simple query.
    Returns True if successful, False otherwise.
    """
    supabase = create_connection()
    if supabase:
        try:
            # Try a simple query
            response = supabase.table('users').select('username').limit(1).execute()
            print("Connection successful!")
            print(f"Found data: {response.data}")
            return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    return False

# For direct testing of this module
if __name__ == "__main__":
    test_connection() 