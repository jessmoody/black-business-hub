from flask import Flask, render_template, flash, redirect, url_for, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from google.cloud.sql.connector import Connector
import sqlalchemy

# initializing Flask app
app = Flask(__name__)
app.config["DEBUG"] = True

# initialize Connector object
connector = Connector()

# function to return the database connection
def getconn() -> pymysql.connections.Connection:
    conn: pymysql.connections.Connection = connector.connect(
        "black-wings-hacks-2023:us-central1:black-wings-hacks-2023-instance",
        "pymysql",
        user="root",
        password="%c@a5LL%PfMj",
        db="listings"
    )
    return conn

# create connection pool
pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)


# Google Cloud SQL (change this accordingly)
PASSWORD ="%c@a5LL%PfMj"
PUBLIC_IP_ADDRESS ="34.170.116.22"
DBNAME ="listings"
PROJECT_ID ="black-wings-hacks-2023"
INSTANCE_NAME ="black-wings-hacks-2023-instance"

# configuration
app.config["SECRET_KEY"] = "yoursecretkey"
app.config["SQLALCHEMY_DATABASE_URI"]= f"mysql + mysqldb://root:{PASSWORD}@{PUBLIC_IP_ADDRESS}/{DBNAME}?unix_socket =/cloudsql/{PROJECT_ID}:{INSTANCE_NAME}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= True

db = SQLAlchemy(app)

# User ORM for SQLAlchemy
class Users(db.Model):
    first_name = db.Column(db.String(100), nullable = False)
    last_name = db.Column(db.String(100), nullable = False)
    business_name = db.Column(db.String(100), nullable = False)
    category = db.Column(db.String(100), nullable = False)
    descrip = db.Column(db.String(100), nullable = False)
    street = db.Column(db.String(100), nullable = False)
    city = db.Column(db.String(100), nullable = False)
    USstate = db.Column(db.String(100), nullable = False)
    zip = db.Column(db.String(100), nullable = False)
    phone = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), primary_key = True,  nullable = False, unique = True)
    website = db.Column(db.String(200), nullable = False)
    social_media = db.Column(db.String(200), nullable = False)

@app.route("/", methods = ['POST','GET'])
def home():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method=='POST':  
        query = request.form.get('query')
        with pool.connect() as db_conn:
            # query database
            result = db_conn.execute("""SELECT * from listings WHERE 
                                        (SELECT category FROM listings WHERE category LIKE '%s' ) OR
                                        (SELECT business_name FROM listings WHERE business_name LIKE '%s') OR
                                        (SELECT city FROM listings WHERE city LIKE '%s' ) OR
                                        (SELECT USstate FROM listings WHERE USstate LIKE '%s' ) OR
                                        (SELECT zip FROM listings WHERE zip LIKE '%s' ),
                                        (query, query, query, query, query)""").fetchall()

            # Do something with the results
            for row in result:
                print(row)

@app.route('/add', methods =['POST', 'GET'])
def add():
    if request.method == 'GET':
        return render_template('addAbusiness.html')
    elif request.method=='POST':    
        # getting name and email
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        business_name = request.form.get('business_name')
        category = request.form.get('category')
        descrip = request.form.get('descrip')
        street = request.form.get('street')
        city = request.form.get('city')
        USstate = request.form.get('USstate')
        zip = request.form.get('zip')
        phone = request.form.get('phone')
        email = request.form.get('email')
        website = request.form.get('website')
        social_media = request.form.get('social_media')

        # insert statement
        insert_stmt = sqlalchemy.text(
            """INSERT INTO listings (first_name, 
                                    last_name, 
                                    business_name,
                                    category,
                                    descrip,
                                    street, 
                                    city,
                                    USstate,
                                    zip,
                                    phone,
                                    email,
                                    website,
                                    social_media) VALUES (:first_name, 
                                                            :last_name, 
                                                            :business_name,
                                                            :category,
                                                            :descrip,
                                                            :street, 
                                                            :city,
                                                            :USstate,
                                                            :zip,
                                                            :phone,
                                                            :email,
                                                            :website,
                                                            :social_media
                                                            )""",
        )

        with pool.connect() as db_conn:
            # insert into database
            db_conn.execute(insert_stmt, 
                            first_name = first_name,
                            last_name = last_name,
                            business_name = business_name,
                            category = category,
                            descrip = descrip,
                            street = street,
                            city = city,
                            USstate = USstate,
                            zip = zip,
                            phone = phone,
                            email = email,
                            website = website,
                            social_media = social_media)

        # checking if user already exists
        user = Users.query.filter_by(email = email).first()

        if not user:
            try:
                # creating Users object
                user = Users(
                    first_name = first_name,
                    last_name =last_name,
                    business_name = business_name,
                    category = category,
                    descrip = descrip,
                    street = street,
                    city = city,
                    USstate = USstate,
                    zip = zip,
                    phone = phone,
                    email = email,
                    website = website,
                    social_media = social_media
                )
                # adding the fields to users table
                db.session.add(user)
                db.session.commit()
                # response
                responseObject = {
                    'status' : 'success',
                    'message': 'Successfully registered.'
                }
                return make_response(responseObject, 200)
            except:
                responseObject = {
                    'status' : 'fail',
                    'message': 'Some error occurred !!'
                }
                return make_response(responseObject, 400)
        else:
            # if user already exists then send status as fail
            responseObject = {
                'status' : 'fail',
                'message': 'User already exists !!'
            }

            return make_response(responseObject, 403)

@app.route('/view')
def view():
    # fetches all the users
    users = Users.query.all()
    # response list consisting user details
    response = list()

    for user in users:
        response.append({
            "first_name" : user.first_name,
            "last_name" : user.last_name,
            "business_name" : user.business_name,
            "category" : user.category,
            "description" : user.description,
            "street" : user.street,
            "city" : user.city,
            "state" : user.state,
            "zip" : user.zip,
            "phone" : user.phone,
            "email": user.email,
            "website" : user.website,
            "social_media" : user.social_media            
        })

    return make_response({
        'status' : 'success',
        'message': response
    }, 200)


@app.route("/donate", methods = ['GET'])
def donate():
    return render_template('donate.html')

@app.route("/about", methods = ['GET'])
def about():
    return render_template('aboutUs.html')

connector.close()

if __name__ == "__main__":
    # serving the app directly
    app.run()