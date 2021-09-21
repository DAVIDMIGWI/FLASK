import re
from tkinter import INSERT

from flask import *
# method 2. view tool window then terminal
# type terminal type: pip install flask
# create the flask object
from pymysql.connections import Connection

app = Flask(__name__)  # __name__ means main
app.secret_key = "^2gt*hy&ui@h&u45"  # 16
# this secret key encrypts your session

# This is the body of your Flask project
# this is the main default route
import pymysql

# establish db connection
connection = pymysql.connect(host="localhost", port=8889, user="root", password="root", database="shoes")


############################################################################################################
@app.route("/shoes")
def shoes():
    # create your query
    sql = "SELECT * FROM products"
    # execute/run
    # create a cursor used to execute sql
    cursor = connection.cursor()
    # now use the cursor to execute your sql.
    cursor.execute(sql)
    # check how many rows were returned
    if cursor.rowcount == 0:
        return render_template("shoes.html", msg="No product found")
    else:
        rows = cursor.fetchall()
        return render_template("shoes.html", rows=rows)


##########################################################################################################
# single shoe
@app.route("/single/<product_id>")
def single(product_id):
    # create your query provide as placeholder
    # create your query
    sql = "SELECT * FROM products WHERE product_id=%s"
    # execute/run
    # create a cursor used to execute sql
    cursor = connection.cursor()
    # now use the cursor to execute your sql.
    # below you provide id to replace the %s
    cursor.execute(sql, product_id)
    # check how many rows were returned
    if cursor.rowcount == 0:
        return render_template("single.html", msg="No product found")
    else:
        row = cursor.fetchone()  # product id was unique.
        return render_template("single.html", row=row)


##########################################################################################################
@app.route("/")
def home():
    return render_template("home.html")


# this is a login route
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        # we now move to the database and confirm if above details exist.
        sql = "SELECT * FROM customers WHERE customer_email=%s and customer_password=%s"
        # create cursor and execute above sql
        cursor = connection.cursor()
        # execute the sql, provide email and password to fit %s placeholders
        cursor.execute(sql, (email, password))
        # check if a match was found.
        if cursor.rowcount == 0:
            return render_template("login.html", error="Check your details and try again")
        elif cursor.rowcount == 1:
            # create a user track of who is logged in
            session["user"] = email
            return redirect("/shoes")

        else:
            return render_template("login.html", error="Error!!!!!!")
    else:
        return render_template("login.html")


##########################################################################################################
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        customer_firstname = request.form["customer_firstname"]
        customer_lastname = request.form["customer_lastname"]
        customer_surname = request.form["customer_surname"]
        customer_email = request.form["customer_email"]
        customer_phone = request.form["customer_phone"]
        customer_password = request.form["customer_password"]
        confirm_password = request.form["confirm_password"]
        customer_gender = request.form["customer_gender"]
        customer_address = request.form["customer_address"]
        customer_dob = request.form["customer_dob"]

        # validation
        import re
        if customer_password != confirm_password:
            return render_template("register.html", password="Password do not match")
        elif len(customer_password) < 6:
            return render_template("register.html", password="password must be 6 characters")
        elif not re.search("[a-z]", customer_password):
            return render_template("register.html", password="Must have a small letter")
        elif not re.search("[A-Z]", customer_password):
            return render_template("register.html", password="Must have a capital letter")
        elif not re.search("[0-9]", customer_password):
            return render_template("register.html", password="Must have a number")
        elif len(customer_phone) < 10:
            return render_template("register.html", phone="Must be above 10 numbers")
        else:
            sql = "insert into customers(`customer_firstname`, `customer_lastname`, `customer_surname`, " \
                  "`customer_email`,`customer_phone`, `customer_password`, `customer_gender`, `customer_address`," \
                  "`customer_dob`)VALUES" "(%s,%s,%s,%s,%s,%s,%s,%s,%s) "
            cursor = connection.cursor()
            # try:
            cursor.execute(sql,
                           (customer_firstname, customer_lastname, customer_surname, customer_email, customer_phone,
                            customer_password, customer_gender, customer_address, customer_dob))
            connection.commit()
            return render_template("register.html", success="saved successfully")
            # except:
            # return render_template("register.html", error="Failed")
    else:
        return render_template("register.html")


##########################################################################################################
@app.route("/logout")
def logout():
    session.pop("user")
    return redirect("/login")

@app.route("/adminlogout")
def adminlogout():
    session.pop("admin")
    return redirect("/admin")


##########################################################################################################
@app.route("/reviews", methods=["POST", "GET"])
def reviews():
    if request.method == "POST":
        user = request.form["user"]
        product_id = request.form["product_id"]
        message = request.form["message"]
        # to a table for reviews
        sql = "insert into reviews(user,product_id,message) values(%s,%s,%s)"
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (user, product_id, message))
            connection.commit()

            flash("Review Posted Successfully")
            return redirect(url_for("single", product_id=product_id))

        except:
            flash("Review Not Posted")
            return redirect(url_for("single", product_id=product_id))

    else:
        return ""


##########################################################################################################
# payment
# modcom.co.ke/sql/payment
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth


@app.route('/mpesa_payment', methods=['POST', 'GET'])
def mpesa_payment():
    if request.method == 'POST':
        phone = str(request.form['phone'])
        amount = str(request.form['amount'])
        # capture the access token
        email = session["user"]

        qtty = str(request.form['qtty'])
        product_id = str(request.form['product_id'])
        total_pay = float(qtty) * float(amount)

        # SQL to insert to sql
        # create a table named payment info
        # pay_id int pk ai
        # phone
        # email
        # qtty
        # total pay
        # product id
        # pay date default current time stamp
        sql = "insert into payment_info(phone,email,qtty,total_pay,product_id)values(%s,%s,%s,%s,%s)"
        cursor = connection.cursor()
        cursor.execute(sql, (phone, email, qtty, total_pay, product_id))
        connection.commit()

        # GENERATING THE ACCESS TOKEN
        consumer_key = "jLoPZqAEPB3JSq9P93PyFbYgML1nqVdV"
        consumer_secret = "ADftWJGRK695PJBB"

        api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"  # AUTH URL
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))

        data = r.json()
        access_token = "Bearer" + ' ' + data['access_token']

        #  GETTING THE PASSWORD
        timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
        passkey = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
        business_short_code = "174379"
        data = business_short_code + passkey + timestamp
        encoded = base64.b64encode(data.encode())
        password = encoded.decode('utf-8')

        # BODY OR PAYLOAD
        payload = {
            "BusinessShortCode": "174379",
            "Password": "{}".format(password),
            "Timestamp": "{}".format(timestamp),
            "TransactionType": "CustomerPayBillOnline",
            "Amount": total_pay,  # use 1 when testing
            "PartyA": phone,  # change to your number
            "PartyB": "174379",
            "PhoneNumber": phone,
            "CallBackURL": "https://modcom.co.ke/job/confirmation.php",
            "AccountReference": email,
            "TransactionDesc": "qtty:" + qtty + "ID:" + product_id
        }

        # POPULAING THE HTTP HEADER
        headers = {
            "Authorization": access_token,
            "Content-Type": "application/json"
        }

        url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"  # C2B URL

        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        return render_template('mpesa_payment.html', msg='Please Complete Payment in Your Phone')
    else:
        return render_template('mpesa_payment.html')


##########################################################################################################
@app.route("/contact", methods=['POST', 'GET'])
def contact():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        message = request.form["message"]

        # we now move to the database and confirm if above details exist.
        sql = "insert into contacts (name,phone,email,message)values(%s,%s,%s,%s)"
        cursor = connection.cursor()
        try:
            cursor.execute(sql, (name, phone, email, message,))
            connection.commit()

            flash("Message Sent Successfully")
            return redirect(url_for("contact"))

        except:
            flash("Message Not Sent")
            return redirect(url_for("contact"))

    else:
        return render_template("contact.html")


##########################################################################################################
# admim
@app.route("/admin", methods=["POST", "GET"])
def admin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        sql = "SELECT * FROM admin WHERE email=%s and password=%s"
        # create cursor and execute above sql
        cursor = connection.cursor()
        # execute the sql, provide email and password to fit %s placeholders
        cursor.execute(sql, (email,password))
        # check if a match was found.
        if cursor.rowcount == 0:
            return render_template("admin.html", error="Check your details and try again")
        elif cursor.rowcount == 1:
            # create a user track of who is logged in
            session["admin"] = email
            return redirect("/dashboard")

        else:
            return render_template("admin.html", error="Error!!!!!!")
    else:
        return render_template("admin.html")


@app.route("/dashboard")
def dashboard():
     if "admin" in session:
         sql="select * from customers"
         cursor=connection.cursor()
         cursor.execute(sql)
         if cursor.rowcount==0:
             return render_template("dashboard.html",msg="no customers")
         else:
             rows=cursor.fetchall()
             return render_template("dashboard.html", rows=rows) # create this template

     else:
        return redirect("/admin")






if __name__ == "__main__":
    app.run(debug=True)
