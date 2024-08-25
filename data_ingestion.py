import os
import pandas as pd
from dotenv import load_dotenv
import psycopg2
import random

# Dummy review text and ratings
sample_reviews = [
    "Absolutely loved this book!",
    "A decent read, but not my favorite.",
    "Not what I expected, but still good.",
    "An amazing story with deep characters.",
    "I couldn't put it down!",
    "Interesting plot, but the pacing was slow.",
    "A classic that everyone should read.",
    "Good, but I've read better.",
    "Fantastic writing, but the ending was predictable.",
    "This book changed my perspective on life."
]

class DataInserter:
    def __init__(self, csv_file):
        # Load environment variables from .env file
        load_dotenv()
        
        # Database connection details
        self.db_host = os.getenv('DB_HOST')
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.db_port = "5432"
        
        # CSV file path
        self.csv_file = csv_file
        
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
            print(f"Error connecting to the database: {e}")
            exit()

    def load_data(self):
        try:
            self.df_book = pd.read_csv(self.csv_file)
            print("Data loaded successfully from CSV.")
        except Exception as e:
            print(f"Error loading data from CSV: {e}")
            exit()

    def insert_data(self):
        # SQL command to insert data
        insert_query = """
            INSERT INTO books (title, author, genre, year_published, summary)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            # Insert each row from the DataFrame into the database
            for index, row in self.df_book.iterrows():
                self.cur.execute(insert_query, (
                    row['Title'], 
                    row['Author'], 
                    row['Genre'], 
                    row['Year Published'], 
                    row['Summary']
                ))
            # Commit the transaction
            self.conn.commit()
            print("Data inserted successfully into Books!")
        except Exception as e:
            print(f"Error inserting data into the database books: {e}")

    def insert_data_reviews(self):  
        try:   
            # SQL command to insert data into the reviews table
            insert_review_query = """
                INSERT INTO reviews (book_id, user_id, review_text, rating)
                VALUES (%s, %s, %s, %s)
            """

            # Insert dummy reviews
            for book_id in range(1, 51):  # Assuming book_id starts at 1 and goes to 50
                for user_id in range(1, 6):  # 5 reviews per book
                    review_text = random.choice(sample_reviews)
                    rating = random.randint(1, 5)
                    self.cur.execute(insert_review_query, (book_id, user_id, review_text, rating))

            # Commit the transaction
            self.conn.commit()
            print("Data inserted successfully into Reviews!")
        except Exception as e:
            print(f"Error inserting data into the database reviews: {e}")

    def close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        print("Database connection closed.")


