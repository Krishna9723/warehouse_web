from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# ------------------ Database Connection ------------------
def connect_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

# ------------------ Initialize DB Table ------------------
def init_db():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name TEXT,
            location TEXT,
            description TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ------------------ Routes ------------------
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    password = request.form['password']
    if password == 'Alance123':
        session['logged_in'] = True
        return redirect(url_for('home'))
    return render_template('login.html', error='Incorrect password')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    location = request.form['location']
    description = request.form['description']

    if name and location and description:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO items (name, location, description) VALUES (%s, %s, %s)", (name, location, description))
        conn.commit()
        conn.close()
    return redirect(url_for('home'))

@app.route('/delete/<int:item_id>')
def delete(item_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id = %s", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

@app.route('/search')
def search():
    query = request.args.get('query')
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE name ILIKE %s", (f"%{query}%",))
    items = cur.fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/all')
def show_all():
    return redirect(url_for('home'))

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit(item_id):
    conn = connect_db()
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        description = request.form['description']
        cur.execute("UPDATE items SET name = %s, location = %s, description = %s WHERE id = %s",
                    (name, location, description, item_id))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    else:
        cur.execute("SELECT * FROM items WHERE id = %s", (item_id,))
        item = cur.fetchone()
        conn.close()
        return render_template('edit.html', item=item)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


