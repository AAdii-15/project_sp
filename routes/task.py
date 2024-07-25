# routes/task.py
from flask import Blueprint, request, jsonify
from db import get_db_connection

task_bp = Blueprint('task', __name__)

@task_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json()
    user_id = data.get('user_id')
    title = data.get('title')
    description = data.get('description')
    due_date = data.get('due_date')
    priority = data.get('priority')
    status = data.get('status', 'pending')  

    if not user_id or not title or not description or not due_date or not priority:
        return jsonify({'message': 'Missing fields'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Database connection error'}), 500

    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO tasks (user_id, title, description, due_date, priority, status)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """, (user_id, title, description, due_date, priority, status))
        task_id = cur.fetchone()[0]
        conn.commit()

        return jsonify({'message': 'Task created successfully', 'task_id': task_id}), 201

    except psycopg2.Error as e:
        print(f"Database operation error: {e}")
        return jsonify({'message': 'Error creating task'}), 500
    finally:
        cur.close()
        conn.close()

@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Database connection error'}), 500

    cur = conn.cursor()

    try:
        cur.execute("SELECT id, user_id, title, description, due_date, priority, status, created_at, updated_at FROM tasks;")
        tasks = cur.fetchall()

        task_list = []
        for task in tasks:
            task_list.append({
                'id': task[0],
                'user_id': task[1],
                'title': task[2],
                'description': task[3],
                'due_date': task[4],
                'priority': task[5],
                'status': task[6],
                'created_at': task[7],
                'updated_at': task[8]
            })

        return jsonify(task_list), 200

    except psycopg2.Error as e:
        print(f"Database operation error: {e}")
        return jsonify({'message': 'Error fetching tasks'}), 500
    finally:
        cur.close()
        conn.close()

@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    due_date = data.get('due_date')
    priority = data.get('priority')
    status = data.get('status')

    if not title or not description or not due_date or not priority or not status:
        return jsonify({'message': 'Missing fields'}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Database connection error'}), 500

    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE tasks
            SET title = %s, description = %s, due_date = %s, priority = %s, status = %s, updated_at = NOW()
            WHERE id = %s;
        """, (title, description, due_date, priority, status, task_id))
        conn.commit()

        if cur.rowcount == 0:
            return jsonify({'message': 'Task not found'}), 404

        return jsonify({'message': 'Task updated successfully'}), 200

    except psycopg2.Error as e:
        print(f"Database operation error: {e}")
        return jsonify({'message': 'Error updating task'}), 500
    finally:
        cur.close()
        conn.close()

@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'message': 'Database connection error'}), 500

    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
        conn.commit()

        if cur.rowcount == 0:
            return jsonify({'message': 'Task not found'}), 404

        return jsonify({'message': 'Task deleted successfully'}), 200

    except psycopg2.Error as e:
        print(f"Database operation error: {e}")
        return jsonify({'message': 'Error deleting task'}), 500
    finally:
        cur.close()
        conn.close()
