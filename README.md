# Shortly
A URL shortener web application

## Description
Shortly is a URL-shortening service developed using Python and Flask frameworks. It allows you to shorten long URLs into compact and shareable links. With Shortly, you can easily create shorter and more manageable URLs for sharing on social media platforms, email, or any other medium.

## How to Run the Project
To run the project, follow these steps:

1. Clone the repository: `git clone <repository_url>`
2. Navigate to the project directory: `cd shortly`
3. Install the dependencies: `pip install -r requirements.txt`
4. Run the application: `python app.py`
5. Access the application in your web browser at: `http://localhost:8000`

Note: Make sure you have Python and Flask installed on your system before running the project.

## Tech Stack Used
Shortly is built using the following technologies:

- Python: A powerful programming language used for backend development.
- Flask: A lightweight web framework for Python.
- Bootstrap 5: A popular CSS framework for building responsive and stylish web interfaces.
- CSS: Cascading Style Sheets for customizing the application's appearance.
- SQLite: A lightweight and embedded database used for storing URL and statistics data.

## The Working
- The application uses SQLite as the database to store URL data and user information.
- It utilizes the Flask framework, along with other packages like hashids for generating short aliases, Flask-Login for user authentication, and Werkzeug for password hashing.
- The application consists of several routes:
-- '/': The main route where authenticated users can shorten URLs. It handles both GET and POST requests. When a POST request is received, it checks if the URL is already present in the database and updates it if necessary. If it's a new URL, it generates a short URL and saves it in the database.
-- '/register': Handles user registration. It saves the username and hashed password in the database.
-- '/login': Handles user login. It compares the provided username and password with the stored values in the database, and if they match, logs the user in.
-- '/logout': Logs out the currently authenticated user.
-- '/<alias>': Redirects the user to the original URL associated with the provided alias.
-- '/stats': Displays the statistics for the URLs created by the currently authenticated user. It retrieves the URL data from the database and generates short URLs for display.
-- '/search': Allows users to search for URLs based on notes, original URLs, or aliases. It retrieves the matching URLs from the database and generates short URLs for display.
-- '/about': Displays information about the application and its author.
- The application utilizes templates (index.html, register.html, login.html, stats.html, search.html, about.html) to render HTML pages with dynamic content.
- User authentication is handled using the User class, which extends the UserMixin class from Flask-Login. It provides methods for loading users from the database and managing user sessions.
- Flash messages are used to display notifications and error messages to the user.
- The application runs on the local development server when the script is executed directly.

## Key Takeaways
- Building a URL shortener using Python and Flask.
- Using SQLite for data storage and retrieval.
- Implementing click tracking and statistics generation.
- Integrating Bootstrap 5 for responsive and appealing user interfaces.

## References
- https://flask.palletsprojects.com/en/2.3.x/
- https://getbootstrap.com/docs/5.0/getting-started/introduction/
- https://www.sqlite.org/index.html
- https://www.w3schools.com/
- https://www.youtube.com/@CodeWithHarry
- https://chozinthet20602.medium.com/authentication-with-flask-login-5d504af3f517
