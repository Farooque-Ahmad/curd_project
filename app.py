from flask import Flask,render_template,request,redirect,url_for,flash,session
import mysql.connector
import mysql.connector.cursor

app = Flask(__name__)
app.secret_key = 'your_secret_key'  

try:

    mydb=mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database='student',
    )
except mysql.connector.Error as err:
    print (f"Error: {err}")
    exit(1)

mycursor = mydb.cursor()

def create_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS register (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(200) NOT NULL,
        email VARCHAR(500) NOT NULL,
        password VARCHAR(500) NOT NULL,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    mycursor.execute(create_table_query)
    mydb.commit()


def create_login_table():
    create_login_table_query = """
    CREATE TABLE IF NOT EXISTS login (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(200) NOT NULL,
        password VARCHAR(500) NOT NULL,
        date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    mycursor.execute(create_login_table_query)
    mydb.commit()

create_table()
create_login_table()


@app.route('/')
def index():
    return render_template('home.html') 

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
    
        sql = "INSERT INTO register (username, email, password) VALUES (%s, %s, %s)"
        val = (username, email, password)
    
        mycursor.execute(sql, val)
        mydb.commit()
    
        flash("Registration successful. Please log in.")
        return redirect(url_for('login'))  # Use url_for for URL generation
     
    else: 
        return render_template('register.html')  # Ensure this template 
    


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        lgmail = request.form['email']
        lpassword = request.form['password']

        # Execute the query with the provided email and password
        sql = "SELECT * FROM register WHERE email = %s AND password = %s"
        val = (lgmail, lpassword)
        mycursor.execute(sql, val)
        user = mycursor.fetchone()

        if user:
            # Fetch all users' data from the database
            mycursor.execute("SELECT * FROM register")
            all_users = mycursor.fetchall()

            # Optionally store user ID or other info in the session
            session['id'] = user[0]  # Assuming the 1st column is user ID

            # Pass all user data to the dashboard
            return render_template("dashboard.html", users=all_users)
        else:
            return render_template("login.html", message="Incorrect email or password")
    
    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    if 'id' in session:
        user_id = session['id']

        mycursor = mysql.connector.cursor()
        mycursor.execute("SELECT * FROM register where id=%s",(user_id))  
        users = mycursor.fetchall()   
        mycursor.close() 

        if users:            
            return render_template('dashboard.html', users=users)  
 
    return render_template('login.html')


@app.route('/delete_user/<int:user_id>', methods=['GET','POST'])
def delete_user(user_id):

   
    sql = "DELETE FROM register WHERE id = %s"
    val = (user_id,)
    mycursor.execute(sql, val)
    mydb.commit()
    
    mycursor.execute("SELECT * FROM register")
    users = mycursor.fetchall()

    
    return render_template('dashboard.html',users=users)


@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="student"
    )
    mycursor = mydb.cursor()
    
    if request.method == 'POST':
        
        username = request.form['username']
        email = request.form['email']

        sql = "UPDATE register SET username = %s, email = %s WHERE id = %s"
        val = (username, email, user_id)
        mycursor.execute(sql, val)
        mydb.commit()

        mycursor.close()
        mydb.close()

        return redirect(url_for('dashboard'))
    
    mycursor.execute("SELECT * FROM register WHERE id = %s", (user_id,))
    user = mycursor.fetchone()

    mycursor.close()
    mydb.close()
    
    return render_template('edit_user.html', user=user)




@app.route('/display')
def display():
    mycursor.execute("select * from register")
    return mycursor.fetchall()
    

if __name__=='__main__':
    app.run(debug=True)

    