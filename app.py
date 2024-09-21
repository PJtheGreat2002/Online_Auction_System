import streamlit as st
import bcrypt
import pandas as pd
from datetime import datetime
from db_manager import add_item_to_auction, get_active_auctions,get_user_bids, get_items_by_auction, register_user, login_user, create_auction, get_user_by_username, place_bid


# User Authentication
def authenticate(username, password):
    user = get_user_by_username(username)
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return user
    return None

# Main Streamlit App
def main():
    st.title("Online Auction System")

    # menu = ["Home", "Login", "Register", "Create Auction", "View Auctions", "Add Items", "Your Bids"]
    # choice = st.sidebar.selectbox("Menu", menu)

    # if choice == "Home":
    #     st.subheader("Welcome to the Online Auction System")

    # elif choice == "Login":
    #     login()

    # elif choice == "Register":
    #     register()

    # elif choice == "Create Auction":
    #     create_auction_page()
    
    # elif choice == "Add Items":
    #     add_items_page()

    # elif choice == "View Auctions":
    #     view_auctions_page()

    # elif choice == "Your Bids":
    #     view_bids_page()
    # Check if the user is logged in
     # Check if the user is logged in
    # Check if the user is logged in
    if 'user_id' in st.session_state:
        page = st.session_state.get('page', "View Auctions")  # Default to "View Auctions"
        
        if page == "View Auctions":
            view_auctions_page()
        elif page == "Add Items":
            add_items_page()  # This should be your function for adding items
        elif page == "Place Bid":
            place_bid_page()  # Call the Place Bid page when selected
        elif page == "Your Bids":
            view_bids_page()
    else:
        # Show login or register options
        option = st.sidebar.radio("Options", ["Login", "Register"])
        if option == "Login":
            login()
        elif option == "Register":
            register()
    
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    
    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.session_state['user_id'] = user[0]
            st.session_state['user_type'] = user[1]
            st.success("Login successful!")
            
            # Redirect based on user type
            if user[1] == 'buyer':
                st.session_state['page'] = "View Auctions"
            elif user[1] == 'seller':
                st.session_state['page'] = "Add Items"

            st.rerun()
        else:
            st.error("Invalid username or password.")   

def register():
    st.title("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    email = st.text_input("Email")
    user_type = st.selectbox("Select User Type", ["buyer", "seller"])
    
    if st.button("Register"):
        if register_user(username, email, password, user_type):
            st.success("Registration successful! Please log in.")
        else:
            st.error("Username already exists.")

def create_auction_page():
    st.subheader("Create a New Auction")
    title = st.text_input("Auction Title")
    description = st.text_area("Description")
    starting_price = st.number_input("Starting Price", min_value=0.0)
    auction_end_time = st.date_input("End Date", min_value=datetime.today())

    if st.button("Create Auction"):
        user_id = 1  # Replace with authenticated user_id in real scenario
        create_auction(title, description, starting_price, auction_end_time, user_id)
        st.success("Auction created successfully!")

#Define Add Items page
def add_items_page():
    st.subheader("Add Items to Auction")
    
    # User needs to provide auction_id to add items
    auction_id = st.number_input("Enter Auction ID to add items to", min_value=1)
    
    if auction_id:
        item_name = st.text_input("Item Name")
        item_description = st.text_area("Item Description")
        starting_bid = st.number_input("Starting Bid", min_value=0.0)
        item_image_url = st.text_input("Image URL (optional)")

        if st.button("Add Item"):
            add_item_to_auction(auction_id, item_name, item_description, starting_bid, item_image_url)
            st.success(f"Item '{item_name}' added to auction ID {auction_id}!")
        
        if st.button("View Auctions"):
            st.session_state['page'] = "View Auctions"
            st.rerun()  # Refresh to show the "View Auctions" page


def view_auctions_page():
    st.subheader("Browse Auctions")
    auctions = get_active_auctions()

    for auction in auctions:
        st.write(f"### {auction['title']}")
        st.write(f"**Current Price:** {auction['current_price']}")
        st.write(f"**Ends On:** {auction['auction_end_time']}")

        # Fetch items for this auction
        items = get_items_by_auction(auction['auction_id'])

        if items:
            # Convert items list to DataFrame for tabular format
            #items_df = pd.DataFrame(items)
            for item in items:
                st.write(f"**{item['name']}**")
                st.write(f"Description: {item['description']}")
                st.write(f"Starting Bid: {item['starting_bid']}")
                
                # Button to place a bid
                if st.button(f"Bid on {item['name']}", key=item['item_id']):
                    # Set the session state to go to the place bid page
                    st.session_state['current_item_id'] = item['item_id']
                    st.session_state['page'] = "Place Bid"
                    st.rerun()  # Redirect to the Place Bid page
            
        else:
            st.write("No items in this auction yet.")
        st.write("---")

# Define a function to place bids
def place_bid_page():
    st.title("Place Your Bid")

    # Retrieve the item ID from the session state
    item_id = st.session_state.get('current_item_id')

    if item_id:
        # Fetch item details using the item_id
        items = get_items_by_auction(item_id)  # This returns a list of items

        # Assuming you want to find the item with the correct item_id
        item = next((i for i in items if i['item_id'] == item_id), None)

        # Check if the item exists
        if item:
            st.subheader(f"Placing bid for: {item['name']}")
            
            # Print the item for debugging purposes
            st.write(f"Item details: {item}")
            
            # Check if 'current_price' exists or use an alternative key like 'starting_bid'
            price_key = 'current_price' if 'current_price' in item else 'starting_bid'
            
            # Convert to float to ensure all inputs are of the same type
            current_price = float(item[price_key])
            starting_bid = float(item['starting_bid'])

            st.write(f"Current Price: {current_price}")

            # Now all arguments for st.number_input are floats
            bid_amount = st.number_input("Enter your bid amount", min_value=starting_bid, format="%.2f")

            if st.button("Confirm Bid"):
                place_bid(item_id, st.session_state['user_id'], bid_amount,)
                st.success("Your bid has been placed successfully!")
        else:
            st.error("Item not found. Please try again.")
            st.write(f"Debug Info: item_id={item_id}, items={items}")
    else:
        st.error("No item selected to place a bid.")
    
    # Optionally add a button to go back to auctions
    if st.button("Back to Auctions"):
        st.session_state['page'] = "View Auctions"
        st.rerun()  # Redirect back to the View Auctions page
    if st.button("Go to your Bids"):
        st.session_state['page'] = "Your Bids"
        st.rerun()  # Redirect back to the View Auctions page


def view_bids_page():
    st.subheader("Your Bids")
    
    user_id = st.session_state.get('user_id')  # Assume user_id is stored in session state after login

    if user_id:
        # Fetch the bids placed by the user
        user_bids = get_user_bids(user_id)

        if user_bids:
            # Convert user bids to DataFrame for display
            user_bids_df = pd.DataFrame(user_bids, columns=['Auction Title', 'Item Name', 'Your Bid'])
            st.table(user_bids_df)
        else:
            st.write("You haven't placed any bids yet.")
    else:
        st.write("Please log in to see your bids.")

if __name__ == '__main__':
    main()
