from flask import Flask, render_template, request, redirect, url_for, session
import bcrypt
import sqlite3

app = Flask(__name__)

# Set the secret key for the session
app.secret_key = 'your_secret_key'

messages = []

# Connect to the SQLite database
conn = sqlite3.connect('users.db')
cur = conn.cursor()

# Create the User table if it doesn't exist
cur.execute('''CREATE TABLE IF NOT EXISTS Users (
    userid INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    age INTEGER NOT NULL,
    number TEXT CHECK(length(number) = 8) NOT NULL,
    address TEXT NOT NULL,
    choice TEXT NOT NULL
);''')

conn.commit()

# Close the database connection
cur.close()
conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        age = request.form['age']
        number = request.form['number']
        address = request.form['address']
        choice = request.form['choice']

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Connect to the SQLite database
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()

        # Insert a new user into the User table
        insert_query = '''
            INSERT INTO Users (name, username, password, age, number, address, choice)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''

        cur.execute(insert_query, (name, username, hashed_password.decode('utf-8'), age, number, address, choice))
        conn.commit()

        # Close the database connection
        cur.close()
        conn.close()

        if choice == "user":
            return redirect(url_for('user_success', name=name))
        elif choice == "volunteer":
            return redirect(url_for('volunteer_success', name=name))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to the SQLite database
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()

        # Retrieve the user from the User table
        select_query = '''
            SELECT * FROM Users WHERE username = ?
        '''

        cur.execute(select_query, (username,))
        user = cur.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
          session['userid'] = user[0]
          
          if user[7] == 'user':
                return redirect(url_for('user_success', name=user[1]))
          elif user[7] == 'volunteer':
                return redirect(url_for('volunteer_success', name=user[1]))
        else:
            return render_template('login.html', message='Invalid username or password')

        # Close the database connection
        cur.close()
        conn.close()

    return render_template('login.html')

@app.route('/success/user/<name>')
def user_success(name):
    return render_template('user_success.html', name=name)

@app.route('/success/volunteer/<name>')
def volunteer_success(name):
    return render_template('volunteer_success.html', name=name)

@app.route('/usercontinue')
def usercontinue_app():
    return render_template('user_page.html')

@app.route('/volunteercontinue')
def volunteercontinue_app():
    return render_template('volunteer_page.html')

@app.route('/chatinterface', methods=['GET', 'POST'])
def chat_interface():
    if request.method == 'POST':
        message = request.form['message']
        if message:
            messages.append(message)
    return render_template('chat_interface.html', messages=messages)

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    if message:
        messages.append(message)
    return redirect(url_for('chat_interface'))

@app.route('/accountprofile')
def accountprofile_app():
    # Check if the user is logged in
    if 'user_id' in session:
        userid = session['userid']
        
        # Connect to the SQLite database
        conn = sqlite3.connect('users.db')
        cur = conn.cursor()

        # Retrieve the user data from the User table based on the user_id
        select_query = '''
            SELECT name, username, age, number, address, choice
            FROM Users
            WHERE userid = ?
        '''

        cur.execute(select_query, (userid,))
        user_data = cur.fetchone()

        # Close the database connection
        cur.close()
        conn.close()

        return render_template('accountprofile.html', name=user_data[0], username=user_data[1], age=user_data[2], number=user_data[3], address=user_data[4], choice=user_data[5])
    
    # If the user is not logged in or user data not found, redirect to the login page
    return redirect(url_for('login'))

@app.route('/location')
def location_app():
    return render_template('location.html')
  
@app.route('/resources')
def resources_app():
    return render_template('resources.html')
  
@app.route('/feedback')
def volunteerfeedback_app():
    return render_template('feedback.html')
  
# Connect to the SQLite database
conn = sqlite3.connect('feedback.db')
cur = conn.cursor()

# Create the Feedback table if it doesn't exist
cur.execute('''CREATE TABLE IF NOT EXISTS Feedback (
    feedbackid INTEGER PRIMARY KEY AUTOINCREMENT,
    userid INTEGER,
    rating INTEGER ,
    comments TEXT,
    timestamp INTEGER,
    FOREIGN KEY (userid) REFERENCES Users(userid)
);''')

conn.commit()

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    rating = request.form['rating']
    comments = request.form['comments']

    userid = session['userid']

    # Store the feedback data in the database
    cur.execute("INSERT INTO Feedback (userid, rating, comments) VALUES (?, ?, ?)", (userid, rating, comments))   
    conn.commit()

    # Optionally, you can provide a confirmation message to the user
    confirmation_message = "Thank you for your feedback!"

    return render_template('feedback.html', confirmation_message=confirmation_message)

if __name__ == '__main__':
    app.run(debug=True, port='81', host='0.0.0.0')
