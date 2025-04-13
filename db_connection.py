# This file is maintained for backwards compatibility
# It now redirects all database connections to use Supabase
from supabase_connection import create_connection as supabase_create_connection

def create_connection():
    """
    Redirects to the Supabase connection for backward compatibility
    
    This function exists for compatibility with existing code that
    was written for MySQL but has been migrated to Supabase.
    
    Returns:
        A Supabase client connection instead of a MySQL connection
    """
    return supabase_create_connection()



