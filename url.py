import requests
from bs4 import BeautifulSoup
import sqlite3
import hashlib
import time
from gnews import GNews

# Initialize GNews
google_news = GNews(language='en', country='US', period='1h', start_date=None, end_date=None,
                    proxy=None)

# List of keywords/topics to search for
topics = ['TECHNOLOGY']

# List of websites to keep
websites_to_keep = {
    'theverge.com',
    'engadget.com',
    'slashgear.com',
    'gizmodo.com',
    'techcrunch.com',
    'thenextweb.com',
    'wired.com',
    'fastcompany.com',
    'anandtech.com',
    'lifehacker.com',
    'pcworld.com',
    'cnet.com',
    'windowscentral.com',
    'androidcentral.com',
    '9to5mac.com',
    'bgr.com',
    'gsmarena.com',
    'macrumors.com',
    '9to5google.com',
    'notebookcheck.net'
}

# Record the start time
start_time = time.time()

# Create a SQLite database and a table to store the processed URLs
db_filename = 'news_data.db'

# Create the SQLite database and processed_urls table if they don't exist
def initialize_database():
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_urls (
            url_hash TEXT UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT,
            original_description TEXT
        )
    ''')
    conn.commit()
    return conn

# Function to compute the SHA-256 hash of a string
def compute_sha256_hash(data):
    sha256 = hashlib.sha256()
    sha256.update(data.encode())
    return sha256.hexdigest()

# Function to check if a URL has been processed
def is_url_processed(url, cursor):
    url_hash = compute_sha256_hash(url)
    cursor.execute('SELECT url_hash FROM processed_urls WHERE url_hash = ?', (url_hash,))
    return cursor.fetchone() is not None

# Function to mark a URL as processed
def mark_url_as_processed(url, cursor):
    url_hash = compute_sha256_hash(url)
    cursor.execute('INSERT INTO processed_urls (url_hash) VALUES (?)', (url_hash,))
    cursor.connection.commit()

# Function to process a single article
def process_article(article_data, conn):
    # Get the URL of the current news article
    news_url = article_data['url']
    cursor = conn.cursor()

    if is_url_processed(news_url, cursor):
        # URL is already processed
        return

    try:
        # Follow redirections until the final destination URL is reached
        response = requests.get(news_url, allow_redirects=True)

        if response.status_code == 200:
            # Use the final URL after redirections
            final_url = response.url

            # Check if the URL belongs to a website in the 'websites_to_keep' set
            if any(website in final_url for website in websites_to_keep):
                # Parse the HTML content of the destination web page
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract the description from the destination web page
                original_description = soup.find('meta', {'name': 'description'})['content']

                # Compute a hash of the article content to check for duplicate articles
                article_content_hash = compute_sha256_hash(original_description)

                # Check if the article with the same content has been processed
                if not is_url_processed(article_content_hash, cursor):
                    mark_url_as_processed(final_url, cursor)
                    mark_url_as_processed(article_content_hash, cursor)
                    result = (final_url, original_description)
                    cursor.execute('''
                        INSERT INTO news (url, original_description) VALUES (?, ?)
                    ''', result)
                    print("Data saved for URL:", result[0])
                else:
                    print("Skipping duplicate article with the same content.")
            else:
                print(f"Skipping URL from {final_url} as it does not belong to the specified websites.")
        elif response.status_code == 403:
            print(f"Access to URL: {news_url} is forbidden (403). Skipping this URL.")
        else:
            print(f"Failed to access the original web page for URL: {news_url}. Status code:", response.status_code)
    except requests.exceptions.RequestException as e:
        print(f"Request Exception occurred for URL: {news_url}. Error: {e}")
    except Exception as ex:
        print(f"An error occurred for URL: {news_url}. Error: {ex}")

# Initialize the database
conn = initialize_database()

# Get the list of news articles from GNews for the current topic
json_resp = google_news.get_news_by_topic(topics[0])

# Process each article sequentially
for article_data in json_resp:
    process_article(article_data, conn)

# Close the SQLite connection
conn.close()

# Calculate the elapsed time
end_time = time.time()
elapsed_time = end_time - start_time
print("Data extraction and saving complete.")
print(f"Elapsed time: {elapsed_time} seconds")
