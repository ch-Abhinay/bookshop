from flask import Flask, render_template, request, redirect, url_for,flash,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime , timezone
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(24)

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
    RegistrationDate = db.Column(db.DateTime, nullable=False,default = datetime.now(timezone.utc))
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

@app.route('/login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(Email=email).first()
        if user and user.PasswordHash == password:
            session['user_id'] = user.UserID
            flash('Login successful!', 'success')
            return redirect('/')  
        else:
            flash('Invalid email or password.', 'danger')
    return render_template('login.html')
@app.route('/logout')
def logout():
    session.pop('user_id', None)  
    flash('You have been logged out.', 'success')
    return redirect('/login')

@app.route('/signin',methods = ['GET','POST'])
def signin():
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        pno = request.form['pno']
        emailid = request.form['emailid']
        passw = request.form['passw']
        sign = User(FirstName = fname,LastName = lname,Email = emailid,PasswordHash = passw,Phone = pno )
        db.session.add(sign)
        db.session.commit()
        session['user_id'] = sign.UserID
        flash('Sign up successful!', 'success')
        return redirect('/')  
    return render_template('signin.html')

if __name__ == '__main__':
    #with app.app_context():
    #    product1 = Products(ProductName='Gilead', Description='Desc-1',Price = 299,StockQuantity = 10,CategoryID = 2)
    #    product2 = Products(ProductName='Spiders Web', Description="Desc-2",Price = 399,StockQuantity = 8,CategoryID = 2)
    #    product3 = Products(ProductName='The one tree', Description='Desc-3',Price = 150,StockQuantity = 10,CategoryID = 2)
    #    product4 = Products(ProductName='The Four Loves', Description='Desc-4',Price = 299,StockQuantity = 10,CategoryID = 2)
#    product1 = Products(ProductName='Gilead', Description='A NOVEL THAT READERS and critics have been eagerly anticipating for over a decade, Gilead is an astonishingly imagined story of remarkable lives. John Ames is a preacher, the son of a preacher and the grandson (both maternal and paternal) of preachers. It’s 1956 in Gilead, Iowa, towards the end of the Reverend Ames’s life, and he is absorbed in recording his family’s story, a legacy for the young son he will never see grow up. Haunted by his grandfather’s presence, John tells of the rift between his grandfather and his father: the elder, an angry visionary who fought for the abolitionist cause, and his son, an ardent pacifist. He is troubled, too, by his prodigal namesake, Jack (John Ames) Boughton, his best friend’s lost son who returns to Gilead searching for forgiveness and redemption. Told in John Ames’s joyous, rambling voice that finds beauty, humour and truth in the smallest of life’s details, Gilead is a song of celebration and acceptance of the best and the worst the world has to offer. At its heart is a tale of the sacred bonds between fathers and sons, pitch-perfect in style and story, set to dazzle critics and readers alike.',Price = 299,StockQuantity = 10,)

    #    db.session.add(product1)
    #    db.session.add(product2)
    #    db.session.add(product3)
    #    db.session.add(product4)
    #    db.session.commit()
    
    app.run(debug=True)