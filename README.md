# Bookshop Application

Welcome to the Bookshop Application! This project is a web application built with Flask that allows users to buy and sell books. Below are the key functionalities and features of the application.

## Features

### 1. Sell Books
Sellers can create an account and list their books for sale on the platform. When listing a book, sellers can provide detailed information such as:
- **Title**: The name of the book.
- **Author**: The author(s) of the book.
- **Genre**: The category or genre the book belongs to.
- **Price**: The selling price of the book.
- **Description**: A brief description or synopsis of the book.
- **Image**: Upload an image of the book cover.

Sellers can manage their inventory by adding new books, updating details of existing books, and removing books that are no longer available. This feature ensures that the book listings are always accurate and up-to-date.

### 2. Buy Books
Buyers can browse the catalog of available books, which includes filtering and sorting options to help them find what they are looking for. Each book has detailed information including:
- **Title**
- **Author**
- **Genre**
- **Price**
- **Description**
- **Book Cover Image**

Buyers can add books to their cart and proceed to checkout. During checkout, buyers can provide shipping details and payment information. Once the purchase is completed, buyers receive an order confirmation and can view their order history.

### 3. Cart
The cart functionality allows buyers to collect books they intend to purchase. Features of the cart include:
- **View Items**: Display all books added to the cart.
- **Update Quantities**: Adjust the quantity of each book.
- **Remove Items**: Remove books from the cart.
- **Persistent Cart**: The cart contents are saved even if the buyer logs out or navigates away from the site, allowing them to continue shopping later.

### 4. Wishlist
The wishlist feature allows buyers to save books they are interested in for future reference. Buyers can:
- **Add Books to Wishlist**: Save books to the wishlist from the book detail page.
- **View Wishlist**: Access a list of all saved books.
- **Remove Books**: Remove books from the wishlist.
- **Move to Cart**: Move books from the wishlist to the cart for purchase.

### 5. Edit Book Details (Seller Only)
Sellers have the capability to update the details of the books they have listed for sale. They can:
- **Edit Book Information**: Change the title, author, genre, price, and description of the book.
- **Update Book Image**: Replace the book cover image with a new one.
- **Deactivate Listings**: Temporarily remove a book from being listed without deleting the information.
- **Delete Listings**: Permanently remove a book from their inventory.

### 6. Rating System
The application includes a star rating system that allows users to rate and review books they have purchased. Features include:
- **Submit Ratings**: Users can rate a book on a scale of 1 to 5 stars.
- **Write Reviews**: Users can provide written feedback along with their star rating.
- **View Ratings and Reviews**: Sellers can view ratings and reviews submitted by other users on the My Ratings page.

### 7. Recommendation System
The application includes a recommendation system that helps users discover new books based on their activity. The system analyzes:
- **Cart Contents**: Books that users have added to their cart.
- **Wishlist**: Books that users have saved to their wishlist.
- **Purchase History**: Books that users have previously purchased.

Based on this data, the system generates personalized book recommendations displayed on the user's dashboard and book catalog page.

## Additional Features

- **User Authentication**: Secure user registration and login system with email verification and password reset options.
- **Edit Profile**: Users can manage their personal information through the profile page. Features include:   Edit name, email, and other personal details.
- **Order History**: Buyers can view a detailed history of their past orders, including order date, items purchased, total amount, and order status.
- **Star Rating System**: Users can rate and review books they have purchased, providing feedback to sellers.
- **Search Functionality**: A powerful search bar allows users to search for books by title making it easy to find specific books.
- **Responsive Design**: The application is designed to be responsive and works well on various devices, including desktops, tablets, and mobile phones.

## Getting Started

To run the project locally, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/ch-Abhinay/bookshop.git
    cd bookshop
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up the database**:
    ```bash
    flask db upgrade
    ```

4. **Run the application**:
    ```bash
    flask run
    ```

5. **Access the application**:
    Open your web browser and navigate to `http://127.0.0.1:5000`.

## Contributing

We welcome contributions to improve the project. If you have suggestions or bug reports, please open an issue on GitHub. For code contributions, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Thank you for using the Bookstore Application! We hope you enjoy your experience.

