from flask import Flask, session, redirect, url_for, request, flash, render_template
from flask import Flask, session, redirect, url_for, request, flash, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import re
import os
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///bookshop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_COOKIE_SECURE'] = True
db= SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    UserID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(100), nullable=False)
    Phone = db.Column(db.String(20), nullable=True)
    RegistrationDate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow )
    UserType = db.Column(db.String(20), nullable=False, default='customer')
    GSTPanNumber = db.Column(db.String(20), nullable=True) 
    Products = db.relationship('Products', backref='merchant', lazy=True)
class Addresses(db.Model):
    __tablename__ = 'addresses'
    AddressID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    StreetAddress= db.Column(db.String(50), nullable=False)
    City= db.Column(db.String(30), nullable=False)
    State= db.Column(db.String(30), nullable=False)
    PostalCode= db.Column(db.String(10), nullable=False)
    Country= db.Column (db.String(50), nullable=False)

class Products(db.Model):
    __tablename__ = 'products'
    ProductID = db.Column(db.Integer, primary_key=True)
    ProductName= db.Column(db.String(50), nullable=False)
    Description= db.Column(db.String(100), nullable=False)
    Price= db.Column(db.Integer, nullable=False)
    StockQuantity= db.Column(db.Integer,nullable=False)
    CategoryID= db.Column(db.Integer,db.ForeignKey('categories.CategoryID'), nullable=False )
    MerchantID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False) 

class Categories(db.Model):
    __tablename__='categories'
    CategoryID= db.Column(db.Integer, primary_key=True)
    CategoryName= db.Column(db.String(50), nullable=False)
    Description= db.Column(db.String(150), nullable=False)

class Carts(db.Model):
    __tablename__='carts'
    CartID= db.Column(db.Integer, primary_key=True)
    UserID= db.Column(db.Integer,db.ForeignKey('users.UserID'), nullable=False)
    CreatedDate= db.Column(db.DateTime, nullable=False)

class CartItems(db.Model):
    __tablename__='cartitems'
    CartItemID= db.Column(db.Integer, primary_key=True)
    CartID= db.Column(db.Integer,db.ForeignKey('carts.CartID'), nullable=False)
    ProductID= db.Column(db.Integer,db.ForeignKey('products.ProductID'), nullable=False)
    Quantity= db.Column(db.Integer, nullable=False)

class Orders(db.Model):
    __tablename__='orders'
    OrderID= db.Column(db.Integer, primary_key=True)
    UserID= db.Column(db.Integer,db.ForeignKey('users.UserID'), nullable=False)
    OrderDate= db.Column(db.DateTime, nullable=False)
    TotalAmount= db.Column(db.Integer,nullable=False)
    ShippingAddressID= db.Column(db.Integer,db.ForeignKey('addresses.AddressID'),nullable=False)
    BillingAddressID= db.Column(db.Integer,db.ForeignKey('addresses.AddressID'),nullable=False)
    OrderStatus= db.Column(db.String(20),nullable=False)

class OrderItems(db.Model):
    __tablename__='orderitems'
    OrderItemID= db.Column(db.Integer, primary_key=True)
    OrderID= db.Column(db.Integer,db.ForeignKey('orders.OrderID'), nullable=False)
    ProductID= db.Column(db.Integer,db.ForeignKey('products.ProductID'), nullable=False)
    Quantity= db.Column(db.Integer, nullable=False)
    UnitPrice= db.Column(db.Integer, nullable=False)

class Payments(db.Model):
    __tablename__='payments'
    PaymentID= db.Column(db.Integer, primary_key=True)
    OrderID= db.Column(db.Integer,db.ForeignKey('orders.OrderID'), nullable=False)
    PaymentDate= db.Column(db.DateTime, nullable=False)
    Amount= db.Column(db.Integer,nullable=False)
    PaymentMethod= db.Column(db.String(50),nullable=False)

class Reviews(db.Model):
    __tablename__='reviews'
    ReviewID= db.Column(db.Integer, primary_key=True)
    ProductID= db.Column(db.Integer,db.ForeignKey('products.ProductID'), nullable=False)
    UserID= db.Column(db.Integer,db.ForeignKey('users.UserID'), nullable=False)
    Rating= db.Column(db.Integer, nullable=False)
    Comment= db.Column(db.String(500), nullable=False)
    ReviewDate= db.Column(db.DateTime, nullable=False)

class Wishlist(db.Model):
    __tablename__='wishlist'
    WishlistID= db.Column(db.Integer, primary_key=True)
    UserID= db.Column(db.Integer,db.ForeignKey('users.UserID'), nullable=False)
    CreatedDate= db.Column(db.DateTime, nullable=False)

class WishlistItems(db.Model):
    __tablename__='wishlistitems'
    WishlistItemID= db.Column(db.Integer, primary_key=True)
    WishlistID= db.Column(db.Integer,db.ForeignKey('wishlist.WishlistID'), nullable=False)
    ProductID= db.Column(db.Integer,db.ForeignKey('products.ProductID'), nullable=False)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/books', methods=['POST','GET'])
def books():
    books = Products.query.all()
    return render_template('books.html', books = books)

@app.route('/contactus')
def contactus():
    return render_template('contactus.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        # print(name,password)
        user= User.query.filter_by(Email=email).first()
        if user and  check_password_hash(user.PasswordHash, password):
            session['user_id'] = user.UserID
            flash('Login successful!', 'success')
            if user.UserType == 'merchant':
                return redirect(url_for('merchant_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    # print(allusers)
    return render_template('login.html')
 
@app.route('/signin', methods=['GET','POST'])
def signin():
    if request.method=='POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
        if not email_pattern.match(email):
            flash('Invalid email address', 'danger')
            return redirect(url_for('signup'))
        password_hash = generate_password_hash(password)
        new_user = User(
            FirstName=first_name,
            LastName=last_name,
            Email=email,
            PasswordHash=password_hash,
            Phone=phone
        )

        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully!', 'success')
        session['user_id']=new_user.UserID
        return redirect(url_for('dashboard'))
    # allusers= Signin.query.all()
    # return render_template('signin.html', allusers=allusers)
    return render_template('signin.html')
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))
    
@app.route('/login1', methods=['POST','GET'])
def login1():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        # print(name,password)
        user= User.query.filter_by(Email=email).first()
        if user and  check_password_hash(user.PasswordHash, password):
            session['user_id'] = user.UserID
            flash('Login successful!', 'success')
            if user.UserType == 'merchant':
                return redirect(url_for('merchant_dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    # print(allusers)
    return render_template('login1.html')

@app.route('/signin1',methods = ['POST','GET'])
def signin1():
    if request.method=='POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        gst_number = request.form['gstnum']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
        if not email_pattern.match(email):
            flash('Invalid email address', 'danger')
            return redirect(url_for('signup'))
        password_hash = generate_password_hash(password)
        new_user = User(
            FirstName=first_name,
            LastName=last_name,
            Email=email,
            PasswordHash=password_hash,
            Phone=phone,
            UserType = 'merchant',
            GSTPanNumber = gst_number
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully!', 'success')
        session['user_id']=new_user.UserID
        return redirect(url_for('merchant_dashboard'))
    return render_template('signin1.html')

@app.route('/merchant_dashboard')
def merchant_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    products = Products.query.filter_by(MerchantID=user.UserID).all()
    return render_template('merchant_dash.html',products = products)

@app.route('/merchant_dashboard/add_book',methods = ['POST','GET'])
def add_book():
    if request.method == "POST":
        bookname = request.form['bookname']
        bookdesc = request.form['bookdesc']
        bookprice = request.form['bookprice']
        stockamount = request.form['stockamount']
        categoryid = request.form['categoryid']
        product = Products(
            ProductName = bookname,
            Description = bookdesc,
            Price = bookprice,
            StockQuantity = stockamount,
            CategoryID = categoryid,
            MerchantID = session.get('user_id')
            )
        db.session.add(product)
        db.session.commit()
    return render_template('add_book.html')

@app.route('/search',methods = ['GET','POST'])
def search():
    if request.method == 'GET':
        query = request.args.get('query')
        if query:
            results = Products.query.filter(Products.ProductName.ilike(f'{query}%')).all()
        else:
            results = []
        return render_template('search_results.html', results=results)
    
if __name__ == '__main__':

    app.run(debug=True)