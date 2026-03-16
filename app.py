from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "telemedicine_secret"


# DATABASE CONNECTION
def get_db():
    conn = sqlite3.connect("telemedicine.db")
    conn.row_factory = sqlite3.Row
    return conn


# CREATE TABLE
conn = sqlite3.connect("telemedicine.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS patients(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
age TEXT,
symptoms TEXT,
condition TEXT,
emergency TEXT,
surgery TEXT,
eta TEXT,
date TEXT,
time TEXT
)
""")

conn.commit()
conn.close()


# HOME
@app.route('/')
def home():
    return render_template("home.html")


# PATIENT PAGE
@app.route('/patient')
def patient():
    return render_template("patient.html")


# DOCTOR LOGIN
@app.route('/doctor_login', methods=['GET','POST'])
def doctor_login():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        if username == "doctor" and password == "1234":
            session['doctor_logged_in'] = True
            return redirect('/doctor')
        else:
            return "Invalid Login"

    return render_template("doctor_login.html")


# SUBMIT PATIENT
@app.route('/submit_patient', methods=['POST'])
def submit_patient():

    name = request.form.get('name')
    age = request.form.get('age')
    symptoms = request.form.get('symptoms')
    condition = request.form.get('condition')
    emergency = request.form.get('status')   # Normal / Serious / Critical
    surgery = request.form.get('surgery')
    eta = request.form.get('eta')
    date = request.form.get('date')
    time = request.form.get('time')

    conn = get_db()

    conn.execute(
        """INSERT INTO patients
        (name,age,symptoms,condition,emergency,surgery,eta,date,time)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (name,age,symptoms,condition,emergency,surgery,eta,date,time)
    )

    conn.commit()
    conn.close()

    return render_template("success.html", name=name)


# DOCTOR DASHBOARD
@app.route('/doctor')
def doctor():

    if not session.get('doctor_logged_in'):
        return redirect('/doctor_login')

    conn = get_db()
    patients = conn.execute("SELECT * FROM patients ORDER BY id DESC").fetchall()
    conn.close()

    return render_template("doctor.html", patients=patients)


# DELETE PATIENT
@app.route('/delete/<int:id>')
def delete(id):

    conn = get_db()
    conn.execute("DELETE FROM patients WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/doctor')


# LOGOUT
@app.route('/logout')
def logout():

    session.pop('doctor_logged_in', None)

    return redirect('/')


# RUN
if __name__ == '__main__':
    app.run(debug=True)