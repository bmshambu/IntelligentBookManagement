from quart import Quart, request, abort, jsonify
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from llama_utils import BookSummaryGenerator
from db_setup import DatabaseManager
from data_ingestion import DataInserter
import os
from dotenv import load_dotenv
import asyncio
import joblib
import numpy as np
import pandas as pd
from functools import wraps
from quart import request, jsonify,make_response


# Load environment variables
load_dotenv()

app = Quart(__name__)

# Database connection details
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PASSWORD_1 = os.getenv('DB_PASSWORD_1')
DB_PORT = "5432"
csv_file_path = 'Data/Book1.csv'

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD_1}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

#print(DATABASE_URL)

# Setup the async SQLAlchemy engine
engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)
print('connected')

# Create tables if they don't exist
db_manager = DatabaseManager()
db_manager.create_tables()
db_manager.close()

# Data ingestion to SQL
data_inserter = DataInserter(csv_file_path)
data_inserter.load_data()
data_inserter.insert_data()
data_inserter.insert_data_reviews()
data_inserter.close()

# Initialize the summary generator
summary_generator = BookSummaryGenerator()


#sample user list
users = {
    "admin": "password123",
    "user": "userpass"
}

def check_auth(username, password):
    """Check if a username/password combination is valid."""
    return users.get(username) == password

def authenticate():
    """Sends a 401 response that enables basic auth."""
    response = make_response(jsonify({"message": "Authentication required."}), 401)
    return response

def requires_auth(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not auth.username or not auth.password or not check_auth(auth.username, auth.password):
            return await authenticate()
        return await f(*args, **kwargs)
    return decorated

@app.route('/books', methods=['POST'])
@requires_auth
async def add_book():
    async with async_session() as session:
        data = await request.json
        title = data.get('title')
        author = data.get('author')
        genre = data.get('genre')
        year_published = data.get('year_published')
        summary = await asyncio.to_thread(summary_generator.generate_summary, data.get('content'))

        stmt = text(
            "INSERT INTO books (title, author, genre, year_published, summary) "
            "VALUES (:title, :author, :genre, :year_published, :summary) "
            "RETURNING id"
        )
        result = await session.execute(
            stmt,
            {
                "title": title,
                "author": author,
                "genre": genre,
                "year_published": year_published,
                "summary": summary,
            },
        )
        book_id = result.scalar_one()
        await session.commit()
        return jsonify({"id": book_id, "summary": summary}), 201

@app.route('/books', methods=['GET'])
@requires_auth
async def get_books():
    try:
        async with async_session() as session:
            stmt = text("SELECT * FROM Books LIMIT 10;")
            result = await session.execute(stmt)
            books = result.mappings().all()
            return jsonify([dict(row) for row in books]), 200
    except Exception as e:
        app.logger.error(f"Error fetching books: {e}")
        return jsonify({"message": "Error fetching books"}), 500

@app.route('/books/<int:id>', methods=['GET'])
@requires_auth
async def get_book(id):
    async with async_session() as session:
        stmt = text("SELECT * FROM books WHERE id = :id")
        result = await session.execute(stmt, {"id": id})
        book = result.mappings().first()
        if not book:
            abort(404)
        return jsonify(dict(book)), 200

@app.route('/books/<int:id>', methods=['PUT'])
@requires_auth
async def update_book(id):
    async with async_session() as session:
        data = await request.json
        title = data.get('title')
        author = data.get('author')
        genre = data.get('genre')
        year_published = data.get('year_published')
        summary = await asyncio.to_thread(summary_generator.generate_summary, data.get('content'))

        stmt = text(
            "UPDATE books SET title = :title, author = :author, genre = :genre, "
            "year_published = :year_published, summary = :summary WHERE id = :id"
        )
        await session.execute(
            stmt,
            {
                "title": title,
                "author": author,
                "genre": genre,
                "year_published": year_published,
                "summary": summary,
                "id": id,
            },
        )
        await session.commit()
        return jsonify({"id": id, "summary": summary}), 200

@app.route('/books/<int:id>', methods=['DELETE'])
@requires_auth
async def delete_book(id):
    async with async_session() as session:
        stmt = text("DELETE FROM books WHERE id = :id")
        await session.execute(stmt, {"id": id})
        await session.commit()
        return '', 204

@app.route('/books/<int:id>/reviews', methods=['POST'])
@requires_auth
async def add_review(id):
    async with async_session() as session:
        data = await request.json
        user_id = data.get('user_id')
        review_text = data.get('review_text')
        rating = data.get('rating')

        stmt = text(
            "INSERT INTO reviews (book_id, user_id, review_text, rating) "
            "VALUES (:book_id, :user_id, :review_text, :rating)"
        )
        await session.execute(
            stmt,
            {
                "book_id": id,
                "user_id": user_id,
                "review_text": review_text,
                "rating": rating,
            },
        )
        await session.commit()
        return jsonify({"book_id": id, "user_id": user_id}), 201

@app.route('/books/<int:id>/reviews', methods=['GET'])
@requires_auth
async def get_reviews(id):
    async with async_session() as session:
        stmt = text("SELECT * FROM reviews WHERE book_id = :book_id")
        result = await session.execute(stmt, {"book_id": id})
        reviews = result.mappings().all()
        return jsonify([dict(row) for row in reviews]), 200

@app.route('/books/<int:id>/summary', methods=['GET'])
@requires_auth
async def get_book_summary(id):
    async with async_session() as session:
        stmt = text("SELECT summary FROM books WHERE id = :id")
        result = await session.execute(stmt, {"id": id})
        book = result.mappings().first()

        stmt_rating = text("SELECT AVG(rating) as avg_rating FROM reviews WHERE book_id = :id")
        result_rating = await session.execute(stmt_rating, {"id": id})
        avg_rating = result_rating.scalar()

        if not book:
            abort(404)
        return jsonify({"summary": book['summary'], "average_rating": avg_rating}), 200

# Load the trained model and scaler
knn = joblib.load('models/knn_model.pkl')
scaler = joblib.load('models/scaler.pkl')
df = pd.read_csv('Data/train_book.csv')

@app.route('/recommendations', methods=['GET'])
@requires_auth
async def get_recommendations():
    genre = request.args.get('genre')
    rating = float(request.args.get('rating'))

    genre_vector = [0, 0, 0, 0]
    if genre == 'Fiction':
        genre_vector[0] = 1
    elif genre == 'Fantasy':
        genre_vector[1] = 1
    elif genre == 'Non-Fiction':
        genre_vector[2] = 1
    elif genre == 'Sci-Fi':
        genre_vector[3] = 1

    sample_input = np.array([[rating] + genre_vector])
    sample_input_scaled = scaler.transform(sample_input)

    distances, indices = await asyncio.to_thread(knn.kneighbors, sample_input_scaled)

    recommended_books = df.iloc[indices[0]]
    recommendations = recommended_books[['Title', 'Author', 'average_rating']].to_dict(orient='records')

    return jsonify(recommendations), 200

@app.route('/generate-summary', methods=['POST'])
@requires_auth
async def generate_summary():
    data = await request.json
    book_content = data.get('content')
    summary = await asyncio.to_thread(summary_generator.generate_summary, book_content)
    return jsonify({"summary": summary}), 200

if __name__ == "__main__":
    app.run(debug=True)
