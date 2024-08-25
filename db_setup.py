import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

class DatabaseManager:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # Database connection details
        self.db_host = os.getenv('DB_HOST')
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_port = "5432"
        
        # Establish database connection
        self.conn = None
        self.cur = None
        
        self.connect()

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                host=self.db_host,
                dbname=self.db_name,
                user=self.db_user,
                password=self.db_password,
                port=self.db_port
            )
            self.conn.autocommit = True
            self.cur = self.conn.cursor()
            print("Database connected successfully.")
        except Exception as e:
            print(f"Error connecting to the database setup: {e}")
            exit()

    def create_tables(self):
        # Create the books table
        create_books_table_query = """
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT NOT NULL,
            year_published INT,
            summary TEXT
        );
        """
        
        # Create the reviews table
        create_reviews_table_query = """
        CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            book_id INT REFERENCES books(id) ON DELETE CASCADE,
            user_id INT NOT NULL,
            review_text TEXT,
            rating INT CHECK (rating >= 1 AND rating <= 5)
        );
        """
        
        try:
            self.cur.execute(create_books_table_query)
            self.cur.execute(create_reviews_table_query)
            print("Tables created successfully.")
        except Exception as e:
            print(f"Error creating tables: {e}")

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed.")


