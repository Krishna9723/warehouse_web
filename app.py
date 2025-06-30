from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def connect_db():
    conn = sqlite3.connect("warehouse.db")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    location TEXT,
                    description TEXT
                )""")
    conn.commit()
    conn.close()

connect_db()

@app.route('/')
def index():
    conn = sqlite3.connect("warehouse.db")
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
        conn = sqlite3.connect("warehouse.db")
        cur = conn.cursor()
        cur.execute("INSERT INTO items (name, location, description) VALUES (?, ?, ?)",
                    (name, location, description))
        conn.commit()
        conn.close()
    return redirect('/')

@app.route('/delete/<int:item_id>')
def delete(item_id):
    conn = sqlite3.connect("warehouse.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/search', methods=['POST'])
def search():
    keyword = request.form['search']
    conn = sqlite3.connect("warehouse.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM items WHERE name LIKE ?", ('%' + keyword + '%',))
    items = cur.fetchall()
    conn.close()
    return render_template('index.html', items=items)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
