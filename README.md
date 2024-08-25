# Quart API Application

This is a Quart-based API application for managing books and reviews.

## Setup

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Virtual environment (optional but recommended)

### Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/bmshambu/IntelligentBookManagement.git
    cd IntelligentBookManagement
    ```

2. Create and activate a virtual environment (optional):

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up environment variables:

    Create a `.env` file in the root directory with the following variables:

    ```
    DB_HOST=your_db_host
    DB_NAME=your_db_name
    DB_USER=your_db_user
    DB_PASSWORD_1=your_db_password
    ```

### Database Setup and running the application

1. Ensure PostgreSQL is running.
2. Create the database and run any necessary migrations:

    ```bash
    python app_sync.py
    ```
