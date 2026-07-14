import streamlit as st
import time
import json
import requests
from streamlit_lottie import st_lottie

# Function to load Lottie animation
def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.RequestException as e:
        st.error(f"⚠️ Failed to load animation: {e}")
        return None

# Use a reliable Lottie animation
lottie_url = "https://assets9.lottiefiles.com/packages/lf20_3rwasyjy.json"
lottie_animation = load_lottieurl(lottie_url)

# Apply full-page gradient background
st.markdown(
    """
    <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #6a11cb, #2575fc);
            color: white;
        }
        .container {
            text-align: center;
            padding: 60px 20px;
        }
        .hero-text {
            font-size: 40px;
            font-weight: bold;
            color: white;
            text-shadow: 2px 2px 10px rgba(0, 0, 0, 0.3);
        }
        .sub-text {
            font-size: 18px;
            color: white;
            margin-top: 10px;
        }
        .glowing-button {
            padding: 15px 30px;
            font-size: 20px;
            color: white;
            background: linear-gradient(90deg, #ff8a00, #e52e71);
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: 0.3s ease-in-out;
            box-shadow: 0px 0px 20px rgba(255, 138, 0, 0.8);
            display: inline-block;
            margin-top: 20px;
        }
        .glowing-button:hover {
            transform: scale(1.1);
            box-shadow: 0px 0px 30px rgba(255, 138, 0, 1);
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Main container
st.markdown("<div class='container'>", unsafe_allow_html=True)
st.markdown("<div class='hero-text'>🚀 Welcome to AI Tutor!</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-text'>Master new skills with personalized learning.</div>", unsafe_allow_html=True)

# Display Lottie animation
if lottie_animation:
    st_lottie(lottie_animation, height=300, key="animation")
else:
    st.error("⚠️ Failed to load animation. Try using a different Lottie URL.")

# Check if the button was clicked
if st.button("Start Learning 🚀", key="start"):
    with st.spinner("Redirecting..."):
        time.sleep(1)  # Simulate loading effect
    st.switch_page("app.py")  # ✅ Redirects to app.py

st.markdown("</div>", unsafe_allow_html=True)
