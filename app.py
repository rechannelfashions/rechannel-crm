from flask import Flask, render_template, request, redirect, url_for, session, Response
from flask_mysqldb import MySQL
import MySQLdb.cursors
import csv
import io

app = Flask(__name__)
app.secret_key = 'rechannel_luxury_secret_key'

# MySQL Configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'rechannel_crm'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

def is_authenticated():
    return 'user_id' in session

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password'
    return render_template('index.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
def index():
    if not is_authenticated():
        return redirect(url_for('login'))
        
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT * FROM appointments ORDER BY id DESC")
        appointments = cur.fetchall()
    except:
        appointments = []

    try:
        cur.execute("SELECT * FROM bookings ORDER BY id DESC")
        bookings = cur.fetchall()
    except:
        bookings = []

    try:
        cur.execute("SELECT * FROM trials ORDER BY id DESC")
        trials = cur.fetchall()
    except:
        trials = []

    cur.close()
    return render_template('index.html', appointments=appointments, bookings=bookings, trials=trials)

# --- APPOINTMENTS API (CRUD) ---
@app.route('/api/appointments', methods=['POST'])
def save_appointment():
    f = request.form
    app_id = f.get('id')
    cur = mysql.connection.cursor()
    if app_id:
        cur.execute("""UPDATE appointments SET customer_name=%s, customer_phone=%s, appointment_date=%s, 
                       appointment_time=%s, order_manager=%s, reference=%s WHERE id=%s""",
                    (f.get('customer_name'), f.get('customer_phone'), f.get('appointment_date'), 
                     f.get('appointment_time'), f.get('order_manager'), f.get('reference'), app_id))
    else:
        cur.execute("""INSERT INTO appointments (customer_name, customer_phone, appointment_date, appointment_time, order_manager, reference) 
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (f.get('customer_name'), f.get('customer_phone'), f.get('appointment_date'), 
                     f.get('appointment_time'), f.get('order_manager'), f.get('reference')))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

@app.route('/api/appointments/delete/<int:id>', methods=['POST'])
def delete_appointment(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM appointments WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

# --- BOOKINGS API (CRUD) ---
@app.route('/api/bookings', methods=['POST'])
def save_booking():
    f = request.form
    b_id = f.get('id')
    cur = mysql.connection.cursor()
    
    params = (
        f.get('order_no', ''), f.get('customer_name', ''), f.get('customer_phone', ''),
        f.get('booking_date') or None, f.get('trial_date') or None, f.get('order_manager', ''),
        1 if 'sw' in f else 0, 1 if 'nw' in f else 0, 1 if 'jp' in f else 0, 
        1 if 'bomber' in f else 0, 1 if 'suit' in f else 0, 1 if 'bundi' in f else 0, 
        1 if 'iw' in f else 0, 1 if 'kurta' in f else 0
    )
    
    if b_id:
        cur.execute("""UPDATE bookings SET order_no=%s, customer_name=%s, customer_phone=%s, booking_date=%s, 
                       trial_date=%s, order_manager=%s, sw=%s, nw=%s, jp=%s, bomber=%s, suit=%s, bundi=%s, iw=%s, kurta=%s WHERE id=%s""",
                    params + (b_id,))
    else:
        cur.execute("""INSERT INTO bookings (order_no, customer_name, customer_phone, booking_date, trial_date, order_manager, 
                       sw, nw, jp, bomber, suit, bundi, iw, kurta) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", params)
    
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

@app.route('/api/bookings/delete/<int:id>', methods=['POST'])
def delete_booking(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM bookings WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

# --- TRIALS API (CRUD) ---
@app.route('/api/trials', methods=['POST'])
def save_trial():
    f = request.form
    t_id = f.get('id')
    cur = mysql.connection.cursor()
    
    params = (
        f.get('order_no', ''), f.get('customer_name', ''), f.get('customer_phone', ''),
        f.get('trial_date') or None, 1 if 'first_trial_done' in f else 0, 
        1 if 'second_trial_done' in f else 0, 1 if 'delivery_done' in f else 0
    )
    
    if t_id:
        cur.execute("""UPDATE trials SET order_no=%s, customer_name=%s, customer_phone=%s, trial_date=%s, 
                       first_trial_done=%s, second_trial_done=%s, delivery_done=%s WHERE id=%s""",
                    params + (t_id,))
    else:
        cur.execute("""INSERT INTO trials (order_no, customer_name, customer_phone, trial_date, first_trial_done, second_trial_done, delivery_done) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""", params)
    
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

@app.route('/api/trials/delete/<int:id>', methods=['POST'])
def delete_trial(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM trials WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

# --- EXCEL EXPORT ROUTES ---
@app.route('/export/<module_name>')
def export_excel(module_name):
    if not is_authenticated():
        return redirect(url_for('login'))
        
    cur = mysql.connection.cursor()
    table_map = {
        'bookings': 'bookings',
        'trials': 'trials',
        'appointments': 'appointments'
    }
    
    target_table = table_map.get(module_name, 'bookings')
    cur.execute(f"SELECT * FROM {target_table}")
    rows = cur.fetchall()
    cur.close()

    output = io.StringIO()
    if rows:
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={module_name}_export.csv"}
    )

if __name__ == '__main__':
    app.run(debug=True)