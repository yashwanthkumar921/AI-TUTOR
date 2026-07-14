import streamlit as st
import json
import hashlib
import os

# Apply global light theme and remove extra white box
st.markdown(
    """
    <style>
        /* Set full-page background to light */
        html, body, section.main {
            background-color: #f8f9fa !important; 
            color: #000 !important; 
        }

        /* Remove white box under "Sign up" */
        .st-emotion-cache-1kyxreq, .st-emotion-cache-18ni7ap {
            background: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }

        /* Force body container to take full width */
        .block-container {
            padding-top: 1rem !important;
            padding-left: 0 !important;
            padding-right: 0 !important;
        }

        /* Center container */
        .container {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }

        /* Form styling */
        .form-container {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            width: 100%;
            max-width: 400px;
        }

        /* Input field styling */
        input {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border: 1px solid #ccc;
            border-radius: 6px;
            font-size: 14px;
        }

        /* Register button styling */
        .register-btn {
            width: 100%;
            background: #4C8BF5;
            color: white;
            padding: 12px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
        }
        .register-btn:hover {
            background: #357AE8;
        }

        /* Login link */
        .login-link {
            text-align: center;
            margin-top: 10px;
            font-size: 14px;
        }
        .login-link a {
            color: #357AE8;
            text-decoration: none;
        }
        .login-link a:hover {
            text-decoration: underline;
        }

        /* Image container */
        .image-container {
            text-align: center;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .image-container img {
            max-width: 90%;
        }

        /* Checkbox alignment */
        .checkbox-container {
            display: flex;
            align-items: center;
            gap: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# User JSON file
USER_FILE = "users.json"

# Load users from JSON
def load_users():
    try:
        with open(USER_FILE, "r") as f:
            users = json.load(f)
            return users if isinstance(users, list) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Save users to JSON
def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# Hash password function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Title without white box
st.markdown(
    "<h2 style='text-align: left; font-size: 28px; font-weight: bold; margin-bottom: 5px;'>Sign up</h2>",
    unsafe_allow_html=True
)

# Layout with two columns (left = form, right = image)
col1, col2 = st.columns([1, 1])

# Left Side - Registration Form
with col1:
    
    username = st.text_input("Username", placeholder="John Doe")
    email = st.text_input("Your Email", placeholder="example@email.com")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    confirm_password = st.text_input("Repeat your password", type="password", placeholder="Confirm your password")

    # Checkbox with proper styling
    agree = st.checkbox("I agree to all statements in Terms of service")

    # Register button
    if st.button("Register", key="register_btn", help="Create your account"):
        if password != confirm_password:
            st.error("Passwords do not match!")
        elif not agree:
            st.error("You must agree to the Terms of Service!")
        else:
            users = load_users()
            if any(user.get("username") == username for user in users):
                st.error("Username already exists!")
            else:
                users.append({"username": username, "email": email, "password": hash_password(password)})
                save_users(users)
                st.success("Registration successful! Redirecting to login...")

                # Redirect to login page
                st.switch_page("pages/2_login.py")

    st.markdown('<div class="login-link">Already a member? <a href="pages/2_login.py">Login here</a></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


