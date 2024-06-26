from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///bookshop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db= SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    UserID = db.Column(db.Integer, primary_key=True)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(100), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(100), nullable=False)
    Phone = db.Column(db.String(20), nullable=True)
    RegistrationDate = db.Column(db.DateTime, nullable=False)
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
    return render_template('books.html')

@app.route('/contactus')
def contactus():
    return render_template('contactus.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signin')
def signin():
    return render_template('signin.html')

if __name__ == '__main__':
    app.run(debug=True)