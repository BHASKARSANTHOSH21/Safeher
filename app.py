from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "safeher123"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'safeher'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            """
            INSERT INTO users(name,email,phone,password)
            VALUES(%s,%s,%s,%s)
            """,
            (name, email, phone, password)
        )

        mysql.connection.commit()
        cur.close()

        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()

        cur.execute(
            """
            SELECT * FROM users
            WHERE email=%s AND password=%s
            """,
            (email, password)
        )

        user = cur.fetchone()

        cur.close()

        if user:

            session['user_id'] = user[0]
            session['name'] = user[1]

            return redirect('/dashboard')

        return "Invalid Email or Password"

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    return render_template(
        'dashboard.html',
        name=session['name']
    )

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/login')

@app.route('/contacts', methods=['GET', 'POST'])
def contacts():

    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':

        contact_name = request.form['contact_name']
        contact_phone = request.form['contact_phone']

        cur = mysql.connection.cursor()

        cur.execute(
            """
            INSERT INTO contacts(user_id,contact_name,contact_phone)
            VALUES(%s,%s,%s)
            """,
            (
                session['user_id'],
                contact_name,
                contact_phone
            )
        )

        mysql.connection.commit()
        cur.close()

        return redirect('/contacts')

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT contact_name,contact_phone
        FROM contacts
        WHERE user_id=%s
        """,
        (session['user_id'],)
    )

    contacts_list = cur.fetchall()

    cur.close()

    return render_template(
        'contacts.html',
        contacts=contacts_list
    )

@app.route('/passengers', methods=['GET', 'POST'])
def passengers():

    if request.method == 'POST':

        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        emergency = request.form['emergency']

        cur = mysql.connection.cursor()

        cur.execute(
            """
            INSERT INTO Passengers
            (Name,Phone,Email,EmergencyContact)
            VALUES(%s,%s,%s,%s)
            """,
            (
                name,
                phone,
                email,
                emergency
            )
        )

        mysql.connection.commit()
        cur.close()

        return redirect('/passengers')

    return render_template('passengers.html')

@app.route('/drivers')
def drivers():

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT *
        FROM Drivers
        """
    )

    drivers = cur.fetchall()

    cur.close()

    return render_template(
        'drivers.html',
        drivers=drivers
    )

@app.route('/trips', methods=['GET', 'POST'])
def trips():

    cur = mysql.connection.cursor()

    if request.method == 'POST':

        passenger = request.form['passenger']
        driver = request.form['driver']
        vehicle = request.form['vehicle']
        start = request.form['start']
        end = request.form['end']

        cur.execute(
            """
            INSERT INTO Trips
            (
                PassengerID,
                DriverID,
                VehicleID,
                StartLocation,
                EndLocation,
                StartTime,
                TripStatus
            )
            VALUES
            (
                %s,%s,%s,%s,%s,
                NOW(),
                'Started'
            )
            """,
            (
                passenger,
                driver,
                vehicle,
                start,
                end
            )
        )

        mysql.connection.commit()

        return redirect('/trips')

    cur.execute(
        """
        SELECT PassengerID, Name
        FROM Passengers
        """
    )

    passengers = cur.fetchall()

    cur.execute(
        """
        SELECT DriverID, Name
        FROM Drivers
        """
    )

    drivers = cur.fetchall()

    cur.execute(
        """
        SELECT VehicleID, VehicleNumber
        FROM Vehicles
        """
    )

    vehicles = cur.fetchall()

    cur.execute(
        """
        SELECT
        TripID,
        PassengerID,
        DriverID,
        VehicleID,
        StartLocation,
        EndLocation,
        TripStatus
        FROM Trips
        ORDER BY TripID DESC
        """
    )

    trip_list = cur.fetchall()

    cur.close()

    return render_template(
        'trips.html',
        passengers=passengers,
        drivers=drivers,
        vehicles=vehicles,
        trips=trip_list
    )

@app.route('/complaints', methods=['GET', 'POST'])
def complaints():

    cur = mysql.connection.cursor()

    if request.method == 'POST':

        passenger = request.form['passenger']
        driver = request.form['driver']
        trip = request.form['trip']
        text = request.form['text']

        cur.execute(
            """
            INSERT INTO Complaints
            (
                PassengerID,
                DriverID,
                TripID,
                ComplaintText,
                ComplaintDate,
                Status
            )
            VALUES
            (
                %s,%s,%s,%s,
                NOW(),
                'Pending'
            )
            """,
            (
                passenger,
                driver,
                trip,
                text
            )
        )

        mysql.connection.commit()

        return redirect('/complaints')

    cur.execute("SELECT PassengerID, Name FROM Passengers")
    passengers = cur.fetchall()

    cur.execute("SELECT DriverID, Name FROM Drivers")
    drivers = cur.fetchall()

    cur.execute("SELECT TripID FROM Trips")
    trips = cur.fetchall()

    cur.close()

    return render_template(
        'complaints.html',
        passengers=passengers,
        drivers=drivers,
        trips=trips
    )

@app.route('/alerts')
def alerts():

    cur = mysql.connection.cursor()

    cur.execute(
        """
        SELECT *
        FROM Alerts
        ORDER BY AlertID DESC
        """
    )

    data = cur.fetchall()

    cur.close()

    return render_template(
        'alerts.html',
        alerts=data
    )

@app.route('/sos')
def dashboard_sos():

    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT TripID
        FROM Trips
        ORDER BY TripID DESC
        LIMIT 1
    """)

    trip = cur.fetchone()

    if not trip:
        cur.close()
        return "No Trip Found"

    cur.execute(
        """
        INSERT INTO Alerts
        (
            TripID,
            AlertType,
            AlertTime,
            AlertStatus
        )
        VALUES
        (
            %s,
            'SOS',
            NOW(),
            'Active'
        )
        """,
        (trip[0],)
    )

    mysql.connection.commit()
    cur.close()

    return redirect('/alerts')

if __name__ == '__main__':
    app.run(debug=True)