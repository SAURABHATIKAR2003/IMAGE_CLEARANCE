import streamlit as st
import sqlite3
import numpy as np
import cv2
from streamlit_option_menu import option_menu

# Create a SQLite database and a table for user information
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )
''')
conn.commit()

def is_username_exists(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    return cursor.fetchone() is not None

def create_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()

def login(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    if user:
        return True
    return False

# Streamlit UI
st.title("Image Deblurring App")

# Sidebar for navigation
with st.sidebar:
    menu = option_menu('Image Deblurring System',

                           ['Register',
                           'Login',
                            'Image Deblurring',
                            'Logout'],
                           icons=['file-earmark-person', 'person', 'images', 'box-arrow-right'],
                           default_index=0)
#menu = st.sidebar.selectbox("Menu", ["Register", "Login", "Image Deblurring", "Logout"])

if menu == "Login":
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(username, password):
            st.success("Logged in as " + username)
            st.session_state.logged_in = True
        else:
            st.error("Invalid username or password")
            st.session_state.logged_in = False

if menu == "Register":
    st.header("Register")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if new_password == confirm_password:
        if st.button("Register"):
            if new_username and new_password:
                if is_username_exists(new_username):
                    st.error('Username already exists. Please choose a different one.')
                else:
                    create_user(new_username, new_password)
                    st.success("Registration successful. You can now log in.")
    else:
        st.error("Passwords do not match")

if menu == "Image Deblurring":
    st.header("Image Deblurring")

    if st.session_state.get("logged_in", False):
        # Upload an image
        uploaded_image = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

        if uploaded_image is not None:
            # Read and display the uploaded image
            image = cv2.imdecode(np.fromstring(uploaded_image.read(), np.uint8), 1)
            st.image(image, caption="Uploaded Image", use_column_width=True)

            # Deblur options
            method = st.selectbox("Select Deblurring Method", ["Select Method", "OpenCV Deblurring"])

            if method == "OpenCV Deblurring":
                kernel = np.array([[-1, -1, -1],
                                   [-1, 9, -1],
                                   [-1, -1, -1]])
                deblurred_image = cv2.filter2D(image, -1, kernel)
                st.image(deblurred_image, caption="Deblurred Image", use_column_width=True)
    else:
        st.warning("Please log in to access image deblurring.")

if menu == "Logout":
    st.session_state.logged_in = False
    st.success("You have been logged out.")

# Close the database connection when the Streamlit app is done
conn.close()