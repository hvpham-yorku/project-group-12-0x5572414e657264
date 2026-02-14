"""
database package – automatically initializes the SQLite database on import.
"""

from src.database.database_setup import initialize_db, close_db

initialize_db()
