from flask import Flask, render_template, request, redirect, url_for, flash
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages
DATABASE = 'database.db'

# Initialize WebDriver (in this case, Chrome)
def init_driver():
    options = Options()
    #options.add_argument('--headless')  # Run Chrome in headless mode
    options.add_argument('--no-sandbox')  # Required in some hosting environments
    options.add_argument('--disable-dev-shm-usage')  # To avoid shared memory issues
    options.add_argument('--disable-gpu')  # Disable GPU hardware acceleration (often needed in headless mode)
    options.add_argument('--window-size=1920x1080')  # Optional, ensures consistent viewport size in headless mode
 
    # Create a Service object and pass it to the WebDriver
    service = Service(ChromeDriverManager().install())
 
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# Function to get the Amazon page content and save to a file
def get_url_data(url):
    
    driver = init_driver()

    # Wait for the page to load completely
    driver.implicitly_wait(10)
    # Open the webpage
    driver.get(url)

    # Wait for a specific element that indicates the page has loaded (e.g., reviews section or a common element)
    try:
        # Wait for a common element on the page to be loaded, like the review section or title
        WebDriverWait(driver, 20).until(  # Wait up to 120 seconds
            EC.presence_of_element_located((By.TAG_NAME, "title_123"))  # Wait for the title element to be present
        )
        print("Page loaded successfully!")
    except TimeoutException:
        print("Timed out waiting for page to load!")

    page_source = driver.page_source

    # Close the WebDriver
    driver.quit()
    return page_source

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

# Initialize the database
def init_db():
    if not os.path.exists(DATABASE):
        with get_db_connection() as conn:
            conn.execute("""
                CREATE TABLE urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL
                )
            """)
        print("Database and table initialized.")

@app.route('/')
def home():
    # Fetch URLs from the database
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT url FROM urls")
        urls = cur.fetchall()
    return render_template('home.html', urls=urls)

@app.route('/add_message', methods=['POST'])
def add_message():
    url = request.form.get('url')
    if url:
        with get_db_connection() as conn:
            # Check if the URL already exists
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM urls WHERE url = ?", (url,))
            exists = cur.fetchone()

            if exists:
                flash("This URL has already been submitted.", "warning")
            else:
                # Insert the new URL into the database
                cur.execute("INSERT INTO urls (url) VALUES (?)", (url,))
                conn.commit()
                flash("URL submitted successfully!", "success")

    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
