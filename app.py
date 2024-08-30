from flask import Flask, session, redirect, url_for, request, flash, render_template,jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
# from flask_login import current_user
import speech_recognition as sr

import re
import os
import speech_recognition as sr
from gtts import gTTS
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///bookshop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db= SQLAlchemy(app)
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

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
#commented
class Products(db.Model):
    __tablename__ = 'products'
    ProductID = db.Column(db.Integer, primary_key=True)
    ProductName= db.Column(db.String(50), nullable=False)
    Author= db.Column(db.String(30), nullable=False)
    Description= db.Column(db.String(100), nullable=False)
    Price= db.Column(db.Integer, nullable=False)
    StockQuantity= db.Column(db.Integer,nullable=False)
    CategoryID= db.Column(db.Integer,db.ForeignKey('categories.CategoryID'), nullable=False )
    MerchantID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False) 
    ProductImage = db.Column(db.String(100), nullable=False)

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
    items = db.relationship('CartItems', backref='cart', lazy=True)
class CartItems(db.Model):
    __tablename__='cartitems'
    CartItemID= db.Column(db.Integer, primary_key=True)
    CartID= db.Column(db.Integer,db.ForeignKey('carts.CartID'), nullable=False)
    ProductID= db.Column(db.Integer,db.ForeignKey('products.ProductID'), nullable=False)
    Quantity= db.Column(db.Integer, nullable=False)
    product = db.relationship('Products', backref=db.backref('cart_items', lazy=True))

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
    CreatedDate= db.Column(db.DateTime, nullable=False , default=datetime.utcnow)
    items = db.relationship('WishlistItems', backref='wishlist', lazy=True)

class WishlistItems(db.Model):
    __tablename__='wishlistitems'
    WishlistItemID= db.Column(db.Integer, primary_key=True)
    WishlistID= db.Column(db.Integer,db.ForeignKey('wishlist.WishlistID'), nullable=False)
    ProductID= db.Column(db.Integer,db.ForeignKey('products.ProductID'), nullable=False)
    product = db.relationship('Products', backref=db.backref('wishlist_items', lazy=True))

vectorizer = TfidfVectorizer(stop_words='english')
def get_user_books():
    if 'user_id' not in session:
        return False
    
    wish=Wishlist.query.filter_by(UserID=session['user_id']).first()
    carts=Carts.query.filter_by(UserID=session['user_id']).first()
    if not wish or not carts :
        return False
    wishlist_books = WishlistItems.query.filter_by(WishlistID=(wish).WishlistID).all()
    cart_books = CartItems.query.filter_by(CartID=(carts).CartID).all()
    return wishlist_books + cart_books

@app.route('/')
def home():
    user_books = get_user_books()
    if not user_books:
        flash('No books in your wishlist or cart.', 'warning')
        return render_template('home.html', recommended_books=[], category_map={})

    books_data = Products.query.all()
    categories = Categories.query.all()
    
    category_map = {category.CategoryID: category.CategoryName for category in categories}

    user_books_data = [f"{book.product.ProductName} {book.product.Description} {book.product.Author}" for book in user_books]
    all_books_data = [f"{book.ProductName} {book.Description} {book.Author}" for book in books_data]
    
    all_books_vectorized = vectorizer.fit_transform(all_books_data)
    user_books_vectorized = vectorizer.transform(user_books_data)
    
    similarities = cosine_similarity(user_books_vectorized, all_books_vectorized)
    average_similarity = similarities.mean(axis=0)
    
    recommended_indices = average_similarity.argsort()[-5:][::-1]  
    recommended_books = [books_data[i] for i in recommended_indices]
    
    return render_template('home.html', recommended_books=recommended_books, category_map=category_map)


@app.route('/books', methods=['POST', 'GET'])
def books():
    books = Products.query.all()
    categories = Categories.query.all()
    category_map = {category.CategoryID: category.CategoryName for category in categories}
    return render_template('books.html', books=books, category_map=category_map)

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
                return redirect(url_for('dashboard'))
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    # print(allusers)
    return render_template('login.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(Email=email).first()
        if user:
            return redirect(url_for('reset_password', user_id=user.UserID))
        else:
            flash('No account found with that email.', 'danger')
    return render_template('forgot_password.html')

@app.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
def reset_password(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form['password']
        user.PasswordHash = generate_password_hash(password)
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', user=user)

 
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

def get_low_stock_products(user_id):
    threshold = 50
    return Products.query.filter_by(MerchantID=user_id).filter(Products.StockQuantity < threshold).all()

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    low_stock_products = get_low_stock_products(user.UserID) if user.UserType == 'merchant' else []
    products = Products.query.filter_by(MerchantID=user.UserID).all()
    return render_template('dashboard.html', user=user, products= products,low_stock_products=low_stock_products)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('login'))  # Redirect to login if user not found

    if request.method == 'POST':
        user.FirstName = request.form['FirstName']
        user.LastName = request.form['LastName']
        user.Email = request.form['Email']
        user.Phone = request.form['Phone']
        if 'GSTPanNumber' in request.form:
            user.GSTPanNumber = request.form['GSTPanNumber']

        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template('edit_profile.html', user=user)


@app.route('/dashboard/my_books')
def my_books():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    user = User.query.get(session['user_id'])
    products = Products.query.filter_by(MerchantID=user.UserID).all()
    categories = Categories.query.all()
    category_map = {category.CategoryID: category.CategoryName for category in categories}
    return render_template('my_books.html', products= products,category_map=category_map)

@app.route('/dashboard/offlineservices', methods=['GET', 'POST'])
def offlineservices():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    products = Products.query.filter_by(MerchantID=user.UserID).all()
    categories = Categories.query.all()
    category_map = {category.CategoryID: category.CategoryName for category in categories}

    if request.method == 'POST':
        book_ids = request.form.getlist('book_id[]')
        quantities = request.form.getlist('quantity[]')

        # Handle form submission for offline services
        for book_id, quantity in zip(book_ids, quantities):
            product = Products.query.filter_by(ProductID=book_id).first()
            if product:
                # Check if stock is sufficient
                if product.StockQuantity >= int(quantity):
                    product.StockQuantity -= int(quantity)
                else:
                    # Handle case where stock is insufficient
                    flash(f'Not enough stock for product: {product.ProductName}', 'danger')
                    return redirect(url_for('offlineservices'))
            else:
                # Handle case where the product is not found
                return f"Book with ID '{book_id}' not found.", 400

        db.session.commit()
        return redirect(url_for('offlineservices'))

    # Retrieve the number of book fields to display
    book_count = int(request.args.get('book_count', 1))
    
    return render_template('offlineservices.html', products=products, category_map=category_map, book_count=book_count)


@app.route('/remove/<int:product_id>', methods=['POST'])
def remove_product(product_id):
    product = Products.query.get(product_id)
    if product:
        # Remove associated cart items
        CartItems.query.filter_by(ProductID=product_id).delete()
        WishlistItems.query.filter_by(ProductID=product_id).delete()
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('my_books'))


@app.route('/update/<int:product_id>', methods=['GET', 'POST'])
def update(product_id):
    product = Products.query.filter_by(ProductID=product_id).first()
    if not product:
        return "Product not found", 404

    if request.method == "POST":
        bookname = request.form['name']
        author = request.form['author']
        bookdesc = request.form['desc']
        bookprice = request.form['price']
        categoryid = request.form['categoryid']
        
        product.ProductName = bookname
        product.Author = author
        product.Description = bookdesc
        product.Price = bookprice
        product.CategoryID = categoryid

        if 'bookimage' in request.files:
            file = request.files['bookimage']
            if file.filename:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                product.ProductImage = filename
        
        db.session.commit()
        return redirect(url_for('my_books'))  # Use url_for for redirection
    
    return render_template('update_book.html', product=product)

@app.route('/dashboard/my_ratings')
def my_ratings():
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    merchant_products = Products.query.filter_by(MerchantID=user_id).all()
    product_ids = [product.ProductID for product in merchant_products]
    
    reviews = Reviews.query.filter(Reviews.ProductID.in_(product_ids)).all()
    
    # Fetch product details
    product_details = {product.ProductID: product.ProductName for product in merchant_products}
    
    return render_template('my_ratings.html', reviews=reviews, product_details=product_details)



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
                return redirect(url_for('dashboard'))
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
        return redirect(url_for('dashboard'))
    return render_template('signin1.html')

# @app.route('/merchant_dashboard')
# def merchant_dashboard():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#     user = User.query.get(session['user_id'])
#     products = Products.query.filter_by(MerchantID=user.UserID).all()
#     return render_template('merchant_dash.html',products = products)

@app.route('/dashboard/add_book', methods=['POST', 'GET'])
def add_book():
    if request.method == 'POST':
        bookname = request.form['bookname']
        author = request.form['author']
        bookdesc = request.form['bookdesc']
        bookprice = request.form['bookprice']
        stockamount = request.form['stockamount']
        categoryid = request.form['categoryid']
        bookimage = request.files['bookimage']

        if bookimage:
            filename = secure_filename(bookimage.filename)
            bookimage.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            product = Products(
                ProductName=bookname,
                Author=author,
                Description=bookdesc,
                Price=bookprice,
                StockQuantity=stockamount,
                CategoryID=categoryid,
                ProductImage=filename,  # Assuming you have this field in your Products model
                MerchantID=session.get('user_id')
            )
            db.session.add(product)
            db.session.commit()
            return redirect(url_for('dashboard'))  # Redirect to a suitable page after adding the book
    return render_template('add_book.html')


@app.route('/search',methods = ['GET','POST'])
def search():
    if request.method == 'GET':
        query = request.args.get('query')
        if query:
            results = Products.query.filter(Products.ProductName.ilike(f'{query}%')).all()
        else:
            results = []
        books = Products.query.all()
        return render_template('search_results.html', results=results)
    
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        flash('please log in first')
        return redirect(url_for('login'))
    quantity= int(request.form['quantity'])
    user_id= session['user_id']
    cart= Carts.query.filter_by(UserID=user_id).first()
    if not cart:
        cart = Carts(UserID=user_id, CreatedDate=datetime.utcnow())
        db.session.add(cart)
        db.session.commit()
    cart_item= CartItems.query.filter_by(CartID=cart.CartID, ProductID=product_id).first()
    if cart_item:
        cart_item.Quantity += quantity
    else:
        cart_item = CartItems(CartID=cart.CartID, ProductID=product_id,Quantity=quantity)
        db.session.add(cart_item)
    db.session.commit()
    flash('item added to card successfully!', 'success')
    return redirect(url_for('mycart'))

@app.route('/mycart')
def mycart():
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    cart = Carts.query.filter_by(UserID=user_id).first()
    if not cart:
        flash('Your cart is empty!', 'info')
        return render_template('cart.html', cart_items=[], product_map={}, category_map={})

    cart_items = CartItems.query.filter_by(CartID=cart.CartID).all()
    product_ids = [item.ProductID for item in cart_items]
    products = Products.query.filter(Products.ProductID.in_(product_ids)).all()
    categories = Categories.query.all()
    
    product_map = {product.ProductID: product for product in products}
    category_map = {category.CategoryID: category.CategoryName for category in categories}

    return render_template('cart.html', cart_items=cart_items, product_map=product_map, category_map=category_map)


@app.route('/update_cart_item/<int:item_id>', methods=['POST'])
def update_cart_item(item_id):
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))
    
    new_quantity = request.form['quantity']
    cart_item = CartItems.query.get(item_id)
    if cart_item:
        cart_item.Quantity = new_quantity
        db.session.commit()
        flash('Item updated successfully!', 'success')
    else:
        flash('Item not found.', 'danger')
    return redirect(url_for('mycart'))

@app.route('/delete_cart_item/<int:item_id>', methods=['POST'])
def delete_cart_item(item_id):
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))
    
    cart_item = CartItems.query.get(item_id)
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from cart.', 'success')
    else:
        flash('Item not found.', 'danger')
    return redirect(url_for('mycart'))

@app.route('/wishlist')
def wishlist():
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    wishlist = Wishlist.query.filter_by(UserID=user_id).first()
    if not wishlist:
        flash('Your wishlist is empty!', 'info')
        return render_template('wishlist.html', wishlist_items=[], category_map={})
    
    wishlist_items = WishlistItems.query.filter_by(WishlistID=wishlist.WishlistID).all()
    
    # Fetch categories to create category_map
    categories = Categories.query.all()
    category_map = {category.CategoryID: category.CategoryName for category in categories}

    return render_template('wishlist.html', wishlist_items=wishlist_items, category_map=category_map)

@app.route('/add_to_wishlist/<int:product_id>', methods=['POST'])
def add_to_wishlist(product_id):
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    wishlist = Wishlist.query.filter_by(UserID=user_id).first()
    if not wishlist:
        wishlist = Wishlist(UserID=user_id)
        db.session.add(wishlist)
        db.session.commit()
    
    wishlist_item = WishlistItems.query.filter_by(WishlistID=wishlist.WishlistID, ProductID=product_id).first()
    if wishlist_item:
        flash('Item already in wishlist.', 'info')
    else:
        wishlist_item = WishlistItems(WishlistID=wishlist.WishlistID, ProductID=product_id)
        db.session.add(wishlist_item)
        db.session.commit()
        flash('Item added to wishlist.', 'success')
    
    return redirect(url_for('wishlist'))

@app.route('/remove_wishlist_item/<int:item_id>', methods=['POST'])
def remove_wishlist_item(item_id):
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))
    
    wishlist_item = WishlistItems.query.get(item_id)
    if wishlist_item:
        db.session.delete(wishlist_item)
        db.session.commit()
        flash('Item removed from wishlist.', 'success')
    else:
        flash('Item not found in wishlist.', 'danger')
    
    return redirect(url_for('wishlist'))
    
@app.route('/orders')
def orders():
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))

    user_id = session['user_id']
    orders = Orders.query.filter_by(UserID=user_id).order_by(Orders.OrderDate.desc()).all()
    return render_template('orders.html', orders=orders)


@app.route('/order_items/<int:order_id>', methods=['GET', 'POST'])
def order_items(order_id):
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))
    
    order = Orders.query.get_or_404(order_id)
    order_items = OrderItems.query.filter_by(OrderID=order_id).all()

    # Fetch product details
    product_details = {item.ProductID: Products.query.get(item.ProductID) for item in order_items}

    if request.method == 'POST':
        item_id = request.form['item_id']
        product_id = request.form['product_id']
        rating = request.form.get(f'rating-{item_id}')  # Use .get() to avoid KeyError
        comment = request.form['comment']

        if rating:
            user_id = session['user_id']

            # Create a new review
            review = Reviews(
                ProductID=product_id,
                UserID=user_id,
                Rating=rating,
                Comment=comment,
                ReviewDate=datetime.utcnow()
            )
            db.session.add(review)
            db.session.commit()

            flash('Rating submitted successfully', 'success')
        else:
            flash('Please provide a rating.', 'danger')

        return redirect(url_for('order_items', order_id=order_id))

    return render_template('order_items.html', order=order, order_items=order_items, product_details=product_details)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    addresses = Addresses.query.filter_by(UserID=user_id).all()
     
    cart = Carts.query.filter_by(UserID=user_id).first()
    cart_items = CartItems.query.filter_by(CartID=cart.CartID).all()

    total_amount = sum(item.Quantity * item.product.Price for item in cart_items)

    if request.method == 'POST':
        if not addresses:
            return redirect(url_for('add_address'))

        
        return redirect(url_for('select_payment'))

    return render_template('checkout.html', addresses=addresses, cart_items=cart_items, total_amount=total_amount)

@app.route('/add_address', methods=['GET', 'POST'])
def add_address():
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    if request.method == 'POST':
        street_address = request.form['street_address']
        city = request.form['city']
        state = request.form['state']
        postal_code = request.form['postal_code']
        country = request.form['country']

        address = Addresses(
            UserID=user_id,
            StreetAddress=street_address,
            City=city,
            State=state,
            PostalCode=postal_code,
            Country=country
        )
        db.session.add(address)
        db.session.commit()
        return redirect(url_for('checkout'))
    
    return render_template('add_address.html')

@app.route('/select_payment', methods=['GET','POST'])
def select_payment():
    return render_template('select_payment.html')

@app.route('/process_payment', methods=['POST'])
def process_payment():
    payment_method = request.form['payment_method']
    
    if payment_method == 'online':
        return redirect(url_for('online_payment'))
    elif payment_method == 'cash':
        return redirect(url_for('cash_payment'))
    else:
        return "Invalid payment method", 400

@app.route('/cash_payment', methods=['GET', 'POST'])
def cash_payment():
    user_id = session['user_id']
    
    cart = Carts.query.filter_by(UserID=user_id).first()
    cart_items = CartItems.query.filter_by(CartID=cart.CartID).all()
    
    # Check stock availability
    for item in cart_items:
        product = Products.query.filter_by(ProductID=item.ProductID).first()
        if product.StockQuantity < item.Quantity:
            flash(f'Not enough stock for product: {product.ProductName}', 'danger')
            return redirect(url_for('mycart'))

    total_amount = sum(item.Quantity * item.product.Price for item in cart_items)
    
    address = Addresses.query.filter_by(UserID=user_id).first()
    shipping_address_id = address.AddressID if address else None
    billing_address_id = address.AddressID if address else None
    
    order = Orders(
        UserID=user_id,
        OrderDate=datetime.utcnow(),
        TotalAmount=total_amount,
        ShippingAddressID=shipping_address_id,
        BillingAddressID=billing_address_id,
        OrderStatus='Completed'
    )
    db.session.add(order)
    db.session.commit()

    for item in cart_items:
        order_item = OrderItems(
            OrderID=order.OrderID,
            ProductID=item.ProductID,
            Quantity=item.Quantity,
            UnitPrice=item.product.Price
        )
        db.session.add(order_item)
        
        # Update stock quantity
        product.StockQuantity -= item.Quantity
        db.session.add(product)
        
    db.session.commit()

    payment = Payments(
        OrderID=order.OrderID,
        PaymentDate=datetime.utcnow(),
        Amount=total_amount,
        PaymentMethod='Cash'
    )
    db.session.add(payment)
    db.session.commit()

    for item in cart_items:
        db.session.delete(item)
    db.session.commit()

    return redirect(url_for('order_confirmation', order_id=order.OrderID))



@app.route('/online_payment', methods=['GET', 'POST'])
def online_payment():
    if 'user_id' not in session:
        flash('Please log in first!', 'danger')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        card_number = request.form['card_number']
        expiry_date = request.form['expiry_date']
        cvv = request.form['cvv']
        
        cart = Carts.query.filter_by(UserID=user_id).first()
        cart_items = CartItems.query.filter_by(CartID=cart.CartID).all()
        
        # Check stock availability
        for item in cart_items:
            product = Products.query.filter_by(ProductID=item.ProductID).first()
            if product.StockQuantity < item.Quantity:
                flash(f'Not enough stock for product: {product.ProductName}', 'danger')
                return redirect(url_for('mycart'))

        total_amount = sum(item.Quantity * item.product.Price for item in cart_items)
        
        address = Addresses.query.filter_by(UserID=user_id).first()
        shipping_address_id = address.AddressID if address else None
        billing_address_id = address.AddressID if address else None
        
        order = Orders(
            UserID=user_id,
            OrderDate=datetime.utcnow(),
            TotalAmount=total_amount,
            ShippingAddressID=shipping_address_id,
            BillingAddressID=billing_address_id,
            OrderStatus='Completed'
        )
        db.session.add(order)
        db.session.commit()

        for item in cart_items:
            order_item = OrderItems(
                OrderID=order.OrderID,
                ProductID=item.ProductID,
                Quantity=item.Quantity,
                UnitPrice=item.product.Price
            )
            db.session.add(order_item)
            
            # Update stock quantity
            product = Products.query.filter_by(ProductID=item.ProductID).first()
            product.StockQuantity -= item.Quantity
            db.session.add(product)
        
        db.session.commit()

        payment = Payments(
            OrderID=order.OrderID,
            PaymentDate=datetime.utcnow(),
            Amount=total_amount,
            PaymentMethod='Online'
        )
        db.session.add(payment)
        db.session.commit()

        for item in cart_items:
            db.session.delete(item)
        db.session.commit()

        return redirect(url_for('order_confirmation', order_id=order.OrderID))

    return render_template('online_payment.html')


@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    order = Orders.query.get(order_id)
    if not order:
        return "Order not found", 404

    order_items = OrderItems.query.filter_by(OrderID=order_id).all()
    items_with_details = []
    for item in order_items:
        product = Products.query.get(item.ProductID)
        items_with_details.append({
            'ProductName': product.ProductName,
            'Quantity': item.Quantity,
            'UnitPrice': item.UnitPrice
        })

    shipping_address = Addresses.query.get(order.ShippingAddressID)
    full_shipping_address = f"{shipping_address.StreetAddress}, {shipping_address.City}, {shipping_address.State}, {shipping_address.PostalCode}, {shipping_address.Country}"

    billing_address = Addresses.query.get(order.BillingAddressID)
    full_billing_address = f"{billing_address.StreetAddress}, {billing_address.City}, {billing_address.State}, {billing_address.PostalCode}, {billing_address.Country}"

    return render_template('order_confirmation.html', order=order, items_with_details=items_with_details, full_shipping_address=full_shipping_address, full_billing_address=full_billing_address)


@app.route('/privacy-policy')
def privacy_policy():
    return render_template('privacy_policy.html')

@app.route('/terms-of-service')
def terms_of_service():
    return render_template('terms_and_conditions.html')

@app.route('/book/<int:product_id>')
def book_restock(product_id):
    product = Products.query.get_or_404(product_id)
    return render_template('book_restock.html', product=product)

@app.route('/update_stock/<int:product_id>', methods=['POST'])
def update_stock(product_id):
    product = Products.query.get_or_404(product_id)
    if 'stock' in request.form:
        try:
            stock = int(request.form['stock'])
            product.StockQuantity += stock
            db.session.commit()
            flash('Stock updated successfully!', 'success')
        except ValueError:
            flash('Invalid stock value', 'danger')
    return redirect(url_for('book_restock', product_id=product_id))

@app.route('/dashboard/transaction_history')
def transaction_history():
    merchant_id = session['user_id']
    # Fetch all products for the current merchant
    products = Products.query.filter_by(MerchantID=merchant_id).all()
    
    transaction_data = []
    total_profit = 0

    for product in products:
        # Fetch all order items for the current product
        order_items = OrderItems.query.filter_by(ProductID=product.ProductID).all()
        
        total_quantity = sum(item.Quantity for item in order_items)
        product_profit = sum(item.Quantity * item.UnitPrice for item in order_items)
        total_profit += product_profit

        transaction_data.append({
            'ProductName': product.ProductName,
            'TotalQuantity': total_quantity,
            'TotalProfit': product_profit
        })

    return render_template('transaction_history.html', transaction_data=transaction_data, total_profit=total_profit)

@app.route('/voice_to_text', methods=['GET', 'POST'])
def voice_to_text():
    return render_template('voice_to_text.html')

@app.route('/text_to_voice', methods=['GET', 'POST'])
def text_to_voice():
    audio_url = None
    if request.method == 'POST':
        text = request.form.get('text')
        if text:
            tts = gTTS(text=text, lang='en')
            filename = 'output.mp3'
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            tts.save(file_path)
            audio_url = url_for('static', filename='uploads/' + filename)

    return render_template('text_to_voice.html', audio_url=audio_url)

@app.route('/process_audio', methods=['POST'])
def process_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        print("Recognizing...")
        try:
            text = recognizer.recognize_google(audio)
            print("You said:", text)
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand what you said.")
            return "Sorry, I couldn't understand what you said."
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
            return f"Could not request results from Google Speech Recognition service; {e}"


if __name__ == '__main__':


    app.run(debug=True)