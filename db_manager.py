import psycopg2
import hashlib
from psycopg2.extras import RealDictCursor

# Connect to PostgreSQL
def get_connection():
    return psycopg2.connect(
        host="localhost",  # Adjust as needed
        database="auction_system_db",
        user="postgres",
        password="1234"
    )
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Fetch all active auctions
def get_active_auctions():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM auctions WHERE auction_end_time > NOW()")
    auctions = cursor.fetchall()
    conn.close()
    return auctions

# Fetch user by username
def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

# Insert a new user
def register_user(username, email, password, user_type):
    conn = get_connection()
    cursor = conn.cursor()
     # Check if the username already exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
    if cursor.fetchone()[0] > 0:
        cursor.close()
        conn.close()
        return False  # User already exists

    try:
        cursor.execute("INSERT INTO users (username, email, password, user_type) VALUES (%s, %s, %s, %s)",
                       (username, email, hash_password(password), user_type))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(e)  # Log the error for debugging
        return False  # Registration failed
    finally:
        cursor.close()
        conn.close()
    
    return True  # Registration successful

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, user_type FROM users WHERE username = %s AND password = %s",
                   (username, hash_password(password)))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user  # Returns (user_id, user_type) if successful, else None

# Create new auction
def create_auction(title, description, starting_price, auction_end_time, user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO auctions (title, description, starting_price, current_price, auction_end_time, created_by) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (title, description, starting_price, starting_price, auction_end_time, user_id))
    conn.commit()
    conn.close()
# Insert a new item into an auction
def add_item_to_auction(auction_id, name, description, starting_bid, image_url=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO items (auction_id, name, description, starting_bid, image_url)
        VALUES (%s, %s, %s, %s, %s)
    """, (auction_id, name, description, starting_bid, image_url))
    conn.commit()
    conn.close()

# Retrieve items by auction ID
def get_items_by_auction(auction_id):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM items WHERE auction_id = %s", (auction_id,))
    items = cursor.fetchall()
    conn.close()
    return items

def place_bid(item_id, user_id, bid_amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO bids (item_id, user_id, bid_amount) 
    VALUES (%s, %s, %s)
    """, (item_id, user_id, bid_amount))
    conn.commit()
    conn.close()

def get_item_by_id(item_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE item_id = %s", (item_id,))
    item = cursor.fetchone()
    conn.close()
    if item:
        return {
            'item_id': item[0],
            'name': item[2],  # Assuming 'name' is the third column
            'description': item[3],
            'starting_bid': item[5] if item[5] is not None else 0.0,  # Default to 0.0 if None
            'current_price': item[4] if item[4] is not None else item[5]  # Default to starting_bid if current_price is None
        }
    return None


def get_user_bids(user_id):
    # Query to fetch user's bids
    query = """
    SELECT a.title, i.name, b.bid_amount
    FROM bids b
    JOIN items i ON b.item_id = i.item_id
    JOIN auctions a ON i.auction_id = a.auction_id
    WHERE b.user_id = %s
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(query, (user_id,))
    user_bids = cursor.fetchall()

    # Clean up
    cursor.close()
    conn.close()
    
    return user_bids

def delete_bid(bid_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM bids WHERE bid_id = %s
    """, (bid_id,))
    conn.commit()
    conn.close()
