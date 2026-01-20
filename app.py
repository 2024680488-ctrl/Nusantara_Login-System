import random
from flask import Flask, render_template, request, redirect, url_for, session # Added session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'super-secret-key' # Required for sessions to work

# --- 1. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('nusantara.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       name TEXT, 
                       role TEXT, 
                       collection TEXT, 
                       timestamp TEXT)''')
    conn.commit()
    conn.close()

# --- 2. AI LOGIC ---
def get_book_recommendation(collection):
    general_books = ["Modern Python Programming", "The Art of Digital Libraries", "Introduction to Data Science", "The Pickwick Papers", "Lighthouse","Contengan Jalan" , "His Last Bow [8 stories]"]
    special_books = ["Hikayat Hang Tuah", "Ancient Maps of Malay Archipelago", "Kitab Tib", "Kitab Rahsia Ejaan Jawi (1929)", "Kitab Kata-kata Melayu", "Sejarah Melayu: Royal Edition"]
    
    if collection == "Special":
        return random.choice(special_books)
    else:
        return random.choice(general_books)

# --- 3. ROUTES ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    name = request.form['name']
    role = request.form['role']
    collection = request.form['collection']
    
    # 1. Check jika user pilih Admin
    if role == 'Admin':
        # Kita buat pop-up atau check simple di sini
        # Untuk fasa ini, kita guna password yang tetap (hardcoded)
        admin_id = request.form.get('admin_id') # Kita kena tambah input ini di index.html
        admin_pass = request.form.get('admin_pass')
        
        if admin_id == "admin123" and admin_pass == "password123":
            session['user_name'] = name
            session['chosen_collection'] = collection
            # Simpan data ke database
            save_to_db(name, role, collection)
            return redirect(url_for('admin_dashboard'))
        else:
            return "Wrong Admin ID or Password! <a href='/'>Try again</a>"
    
    # 2. Jika user biasa (Student/Staff/etc)
    session['user_name'] = name
    session['chosen_collection'] = collection
    save_to_db(name, role, collection)
    
    rec_book = get_book_recommendation(collection)
    return render_template('user_view.html', name=name, role=role, rec=rec_book, collection=collection)

# Fungsi bantuan supaya kod login nampak kemas
def save_to_db(name, role, collection):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('nusantara.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO attendance (name, role, collection, timestamp) VALUES (?, ?, ?, ?)",
                   (name, role, collection, time_now))
    conn.commit()
    conn.close()

@app.route('/dashboard')
def admin_dashboard():
    conn = sqlite3.connect('nusantara.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance ORDER BY id DESC")
    all_data = cursor.fetchall()
    total_logins = len(all_data)
    conn.close()
    
    display_name = session.get('user_name', 'Admin')
    
    # FIX: Define the variable by pulling it from the session
    # If the session is empty, it will default to "General"
    chosen_collection = session.get('chosen_collection', 'General') 
    
    # Use the variable to get the right book list
    rec_book = get_book_recommendation(chosen_collection)
    
    return render_template('dashboard.html', 
                           name=display_name, 
                           role="Admin", 
                           rec=rec_book, 
                           logs=all_data, 
                           total=total_logins, 
                           collection=chosen_collection)

@app.route('/delete/<int:id>')
def delete_attendance(id):
    conn = sqlite3.connect('nusantara.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/edit/<int:id>')
def edit_page(id):
    conn = sqlite3.connect('nusantara.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    return render_template('edit.html', data=row)

@app.route('/update', methods=['POST'])
def update_data():
    id = request.form['id']
    name = request.form['name']
    role = request.form['role']
    conn = sqlite3.connect('nusantara.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE attendance SET name=?, role=? WHERE id=?", (name, role, id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    init_db()
    # Port 10000 is default for Render
    app.run(host='0.0.0.0', port=10000)