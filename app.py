from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "telemedicine_secret"

def get_db():
    conn = sqlite3.connect("telemedicine.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            symptoms TEXT,
            description TEXT,
            condition TEXT,
            surgery TEXT,
            eta TEXT,
            emergency TEXT,
            date TEXT,
            time TEXT,
            doctor_reply TEXT
        )
    """)
    conn.commit()
    conn.close()

create_table()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/patient', methods=['GET', 'POST'])
def patient():
    conn = get_db()
    cursor = conn.cursor()
    if request.method == 'POST':
        data = (
            request.form['name'],
            request.form['age'],
            request.form['symptoms'],
            request.form['description'],
            request.form['condition'],
            request.form['surgery'],
            request.form['eta'],
            request.form['emergency'],
            request.form['date'],
            request.form['time']
        )
        cursor.execute("""
            INSERT INTO patients 
            (name, age, symptoms, description, condition, surgery, eta, emergency, date, time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, data)
        conn.commit()
        tracking_id = cursor.lastrowid
        conn.close()
        return render_template('success.html', tracking_id=tracking_id)
    cursor.execute("SELECT * FROM patients ORDER BY id DESC")
    patients = cursor.fetchall()
    conn.close()
    return render_template('patient.html', patients=patients)

@app.route('/track', methods=['GET', 'POST'])
def track():
    if request.method == 'POST':
        tracking_id = request.form.get('tracking_id', '').strip()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (tracking_id,))
        patient = cursor.fetchone()
        conn.close()
        if patient:
            return render_template('patient_details.html', patient=patient)
        else:
            return render_template('track.html', error="No patient found with that ID.")
    return render_template('track.html')

# ✅ Moved here - BEFORE app.run()
@app.route('/patient_details')
def patient_details():
    return redirect('/track')

@app.route('/doctor_login', methods=['GET', 'POST'])
def doctor_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'doctor' and password == '1234':
            session['doctor'] = True
            return redirect('/doctor')
        else:
            return render_template('doctor_login.html', error="Invalid credentials.")
    return render_template('doctor_login.html')

@app.route('/doctor')
def doctor():
    if not session.get('doctor'):
        return redirect('/doctor_login')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients ORDER BY id DESC")
    patients = cursor.fetchall()
    conn.close()
    return render_template('doctor.html', patients=patients)

@app.route('/reply/<int:id>', methods=['POST'])
def reply(id):
    if not session.get('doctor'):
        return redirect('/doctor_login')
    reply_text = request.form['reply']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE patients SET doctor_reply = ? WHERE id = ?", (reply_text, id))
    conn.commit()
    conn.close()
    return redirect('/doctor')

@app.route('/delete/<int:id>')
def delete(id):
    if not session.get('doctor'):
        return redirect('/doctor_login')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/doctor')

@app.route('/logout')
def logout():
    session.pop('doctor', None)
    return redirect('/')

# ✅ app.run() is always last
if __name__ == '__main__':
    app.run(debug=True)