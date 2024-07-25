# routes/auth.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({'message': 'Missing fields'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Database connection error'}), 500

    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM users WHERE username = %s OR email = %s;", (username, email))
        existing_user = cur.fetchone()

        if existing_user:
            return jsonify({'message': 'User already exists'}), 400

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s);", (username, email, hashed_password))
        conn.commit()

        return jsonify({'message': 'User registered successfully'}), 201

    except psycopg2.IntegrityError as e:
        print(f"IntegrityError: {e}")
        return jsonify({'message': 'Integrity error during registration'}), 500
    except psycopg2.Error as e:
        print(f"Database operation error: {e}")
        return jsonify({'message': 'Error registering user'}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'message': 'Error registering user'}), 500
    finally:
        cur.close()
        conn.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': 'Missing fields'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Database connection error'}), 500

    cur = conn.cursor()

    try:
        cur.execute("SELECT password FROM users WHERE username = %s;", (username,))
        user = cur.fetchone()

        if user and check_password_hash(user[0], password):
            return jsonify({'message': 'Login successful'}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401

    except psycopg2.Error as e:
        print(f"Database operation error: {e}")
        return jsonify({'message': 'Error logging in'}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'message': 'Error logging in'}), 500
    finally:
        cur.close()
        conn.close()
