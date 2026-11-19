from flask import Flask, render_template, jsonify
import mysql.connector

app = Flask(__name__, template_folder='../../src/frontend')

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '676767', 
    'database': 'phone_book_db'
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/contacts')
def get_contacts():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contacts")
    contacts = cursor.fetchall()
    conn.close()
    return jsonify(contacts)

if __name__ == '__main__':
    app.run(debug=True)