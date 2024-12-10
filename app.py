from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database initialization
def init_db():
    with sqlite3.connect('database.db') as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL
        )
        """)
    print("Database initialized.")

@app.route('/')
def home():
    # Fetch messages from the database
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT name, message FROM messages")
        messages = cur.fetchall()
    return render_template('home.html', messages=messages)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/add_message', methods=['POST'])
def add_message():
    name = request.form.get('name')
    message = request.form.get('message')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO messages (name, message) VALUES (?, ?)", (name, message))
        conn.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
