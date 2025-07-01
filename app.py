from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
PASSWORD = 'Alance123'

def init_db():
    conn = sqlite3.connect('warehouse.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect('/home')
        else:
            return render_template('login.html', error="Invalid password")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/home')
def index():
    if not session.get('logged_in'):
        return redirect('/')
    conn = sqlite3.connect('warehouse.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM items")
    items = cur.fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add', methods=['POST'])
def add():
    if not session.get('logged_in'):
        return redirect('/')
    name = request.form['name']
    location = request.form['location']
    description = request.form['description']
    if name.strip() and location.strip() and description.strip():
        conn = sqlite3.connect('warehouse.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO items (name, location, description) VALUES (?, ?, ?)",
                    (name, location, description))
        conn.commit()
        conn.close()
    return redirect('/home')

@app.route('/delete/<int:item_id>')
def delete(item_id):
    if not session.get('logged_in'):
        return redirect('/')
    conn = sqlite3.connect('warehouse.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return redirect('/home')

@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit(item_id):
    if not session.get('logged_in'):
        return redirect('/')
    conn = sqlite3.connect('warehouse.db')
    cur = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        description = request.form['description']
        cur.execute("UPDATE items SET name=?, location=?, description=? WHERE id=?",
                    (name, location, description, item_id))
        conn.commit()
        conn.close()
        return redirect('/home')
    cur.execute("SELECT * FROM items WHERE id=?", (item_id,))
    item = cur.fetchone()
    conn.close()
    return render_template('edit.html', item=item)

@app.route('/search')
def search():
    if not session.get('logged_in'):
        return redirect('/')
    query = request.args.get('query', '')
    conn = sqlite3.connect('warehouse.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE name LIKE ?", ('%' + query + '%',))
    items = cur.fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/all')
def all_items():
    return redirect('/home')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
