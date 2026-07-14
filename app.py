import streamlit as st
import json
import os
from datetime import datetime, timedelta
from transformers import AutoModelForCausalLM, AutoTokenizer
from werkzeug.security import generate_password_hash, check_password_hash

import torch
import time
import hashlib


# Check if the page is app.py and hide menu
if "current_page" in st.session_state and st.session_state["current_page"] == "app":
    hide_menu = """
        <style>
            [data-testid="stSidebarNav"] ul {
                display: none;
            }
        </style>
    """
    st.markdown(hide_menu, unsafe_allow_html=True)

# Set the current page
st.session_state["current_page"] = "app"




# ✅ Initialize session state if not set
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None

# ✅ If user is not logged in, start with registration
if not st.session_state["logged_in"]:
    st.switch_page("pages/1_register.py")







# Sidebar with purple-pink gradient and larger menu
st.markdown(
    """
    <style>
    /* Hover effect for lesson and quiz cards */
.lesson-card, .quiz-card {
    background-color: #2d1b5a;
    border-radius: 15px;
    padding: 20px;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    cursor: pointer;
}

.lesson-card:hover, .quiz-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 10px 20px rgba(255, 255, 255, 0.2);
}

    /* Sidebar (menu area) background with gradient */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #5b2c98, #c33764) !important;  /* Purple to pink gradient */
        border-right: 3px solid #000000;  /* Black border */
        color: #000000;  /* Black text */
        padding: 30px;  /* Increased padding for a larger menu */
        font-size: 20px;  /* Larger font size */
        width: 300px;  /* Increase sidebar width */
    }

    /* Remove any glowing or shadows */
    * {
        box-shadow: none !important;
        text-shadow: none !important;
    }

    /* Sidebar menu item styles */
    [data-testid="stSidebar"] .css-1v0mbdj, [data-testid="stSidebar"] .css-1v0mbdj:hover {
        background-color: transparent;
        color: #000000 !important;  /* Black text for menu items */
    }

    /* Main app background */
    .stApp {
        background: linear-gradient(135deg, #1b0c3b, #000000);  /* Deep purple to black */
    }

    /* Header text style for 'AI Tutor for Programming' */
    h1 {
        color: #000000;
        font-weight: 900;
        text-shadow: none;
    }

    /* Lesson headers */
    h2 {
        color: #ffffff;
        font-weight: bold;
    }

     /* Animated streak counter */
    .streak-counter {
        font-size: 36px;
        font-weight: bold;
        color: #FFD700;
        text-align: center;
        animation: pop 0.5s ease-in-out infinite alternate;
    }

    @keyframes pop {
        from {
            transform: scale(1);
        }
        to {
            transform: scale(1.1);
        }
    }
    /* Badge Unlock Notification */
    .badge-popup {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background-color: #4CAF50;  /* Green background */
        color: white;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        font-size: 18px;
        animation: slideIn 0.5s ease-out, fadeOut 0.5s ease-in 4s forwards;
        z-index: 1000;
    }

    /* Slide-in animation */
    @keyframes slideIn {
        from {
            transform: translateX(100%);
        }
        to {
            transform: translateX(0);
        }
    }

    /* Fade-out animation */
    @keyframes fadeOut {
        to {
            opacity: 0;
            visibility: hidden;
        }
    }
    input, textarea {
        background: linear-gradient(145deg, #2d1b5a, #3a1d6e);
        border-radius: 10px;
        padding: 10px;
        color: #fff;
        border: none;
        box-shadow: 3px 3px 5px #1b1033, -3px -3px 5px #3a1d6e;
    }

    button {
        background-color: #6c5ce7;
        border-radius: 10px;
        padding: 10px 20px;
        color: #fff;
        font-weight: bold;
        transition: all 0.3s ease;
        border: none;
    }
    button:hover {
        background-color: #a29bfe;
        box-shadow: 0 8px 16px rgba(108, 92, 231, 0.4);
        transform: translateY(-3px);
    }

    @keyframes typing {
        from { width: 0 }
        to { width: 100% }
    }

    h1 {
        overflow: hidden;
        white-space: nowrap;
        border-right: 3px solid #fff;
        width: 0;
        animation: typing 3s steps(30, end) forwards;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load and Save JSON Data
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def save_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Initialize Progress File if Missing
progress_file = "user_data/progress.json"
if not os.path.exists(progress_file):
    initial_data = {
        "completed_lessons": [],
        "quiz_scores": {},
        "last_learning_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "streak_count": 1,
        "badges": [],
        "learning_goal": {}
    }
    os.makedirs(os.path.dirname(progress_file), exist_ok=True)  # Create user_data directory if it doesn't exist
    save_json(initial_data, progress_file)
else:
    # If the file exists, load and check for missing keys
    progress = load_json(progress_file)
    if "badges" not in progress:
        progress["badges"] = []
    if "learning_goal" not in progress:
        progress["learning_goal"] = {}
    if "quiz_scores" not in progress:
        progress["quiz_scores"] = {}
    save_json(progress, progress_file)

# Load Progress
progress = load_json(progress_file)



# Streak System
def update_streak():
    try:
        # Try parsing with timestamp format
        last_learning_time = datetime.strptime(progress["last_learning_time"], "%Y-%m-%d %H:%M:%S")
    except ValueError:
        # Fallback to date-only format
        last_learning_time = datetime.strptime(progress["last_learning_time"], "%Y-%m-%d")
    
    today = datetime.now().date()
    if last_learning_time.date() == today:
        return  # Already interacted today

    # Check if yesterday was the last learning day
    if (today - last_learning_time.date()).days == 1:
        progress["streak_count"] += 1
    else:
        progress["streak_count"] = 1  # Reset streak

    # Update last learning time
    progress["last_learning_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_json(progress, progress_file)
  # Display the pop-up notification
def show_badge_popup(badge_name):
    st.markdown(
        f"""
        <div class="badge-popup">
            🎉 New Badge Unlocked: <strong>{badge_name}</strong>!
        </div>
        """,
        unsafe_allow_html=True
    )
# Badge System
def check_badges():
    # Ensure the 'badges' key exists
    if "badges" not in progress:
        progress["badges"] = []

    badges = progress["badges"]
    if "Lesson Master" not in badges:
        badges.append("Lesson Master")
        show_badge_popup("Lesson Master")

    # Badge: Complete all lessons
    if len(progress["completed_lessons"]) == len(lessons) and "Lesson Master" not in badges:
        badges.append("Lesson Master")

    # Badge: Score 100% on a quiz
    for score in progress["quiz_scores"].values():
        if score == 100 and "Quiz Champ" not in badges:
            badges.append("Quiz Champ")
            break

    # Badge: Maintain a streak of 7 days
    if progress["streak_count"] >= 7 and "Streak Star" not in badges:
        badges.append("Streak Star")

    progress["badges"] = badges
    save_json(progress, progress_file)

    # Animated Streak Counter
def live_streak_counter(streak_count):
    streak_placeholder = st.empty()
    for _ in range(10):  # Simulate a live update (for demo purposes)
        streak_placeholder.markdown(
            f"<div class='streak-counter'>Streak: {streak_count} Days 🔥</div>",
            unsafe_allow_html=True
        )


# Hugging Face Model Initialization
@st.cache_resource
def load_hugging_face_model():
    model_name = "Salesforce/codegen-350M-mono"  # Programming-specific model
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16)
    return tokenizer, model

tokenizer, model = load_hugging_face_model()

# Clean Response Function
def clean_response(response):
    lines = response.split("\n")
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line and line not in cleaned_lines:
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines)

# Get Hugging Face Response
def get_hf_response(question):
    prompt = (
        "You are a Python programming assistant. Provide accurate answers to questions about Python and include examples. "
        "For example:\n\n"
        "Q: How do I add two variables in Python?\n"
        "A: To add two variables in Python, you can use the + operator. For example:\n"
        "```python\n"
        "a = 5\n"
        "b = 10\n"
        "c = a + b\n"
        "print(c)  # Output: 15\n"
        "```\n\n"
        f"Q: {question}\n"
        "A:"
    )
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(
            inputs["input_ids"],
            max_length=250,
            num_return_sequences=1,
            repetition_penalty=1.2,
            temperature=0.7,
        )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return clean_response(response.split("A:")[-1].strip())

# Check User Answers
def check_answers(questions, user_answers):
    score = 0
    for i, question in enumerate(questions):
        if user_answers[i] == question["answer"]:
            score += 1
    return score

# Lessons and Quizzes
lessons = [
    {"title": "Introduction to Python", "file": "lessons/intro_to_python.json"},
    {"title": "Variables and Data Types", "file": "lessons/variables_and_data_types.json"},
    {"title": "Conditionals in Python", "file": "lessons/conditionals.json"},
    {"title": "Loops in Python", "file": "lessons/loops.json"},
    {"title": "Functions in Python", "file": "lessons/functions.json"}
]

quizzes = [
    {"title": "Quiz: Introduction to Python", "file": "quizzes/intro_to_python_quiz.json"},
    {"title": "Quiz: Variables and Data Types", "file": "quizzes/variables_and_data_types_quiz.json"},
    {"title": "Quiz: Conditionals", "file": "quizzes/conditionals_quiz.json"},
    {"title": "Quiz: Loops", "file": "quizzes/loops_quiz.json"},
    {"title": "Quiz: Functions", "file": "quizzes/functions_quiz.json"}
]

# App Layout
st.title("AI Tutor for Programming in python")

# Update streak and badges
update_streak()
check_badges()
# Display the pop-up notification
def show_badge_popup(badge_name):
    st.markdown(
        f"""
        <div class="badge-popup">
            🎉 New Badge Unlocked: <strong>{badge_name}</strong>!
        </div>
        """,
        unsafe_allow_html=True
    )


menu = st.sidebar.radio("Menu", ["📚Lesson", "💡Quiz", "⌛Set Learning Goal", "📈Progress","💬Chatbot"])

# Set Learning Goal
# Set Learning Goal
if menu == "⌛Set Learning Goal":
    st.header("Set Your Learning Goal")
    
    goal_description = st.text_input("🎯 What is your learning goal?", "Complete Python basics in 2 weeks")
    duration = st.number_input("⏳ How many days do you want to complete it in?", min_value=1, max_value=30, value=14)

    if st.button("Set Goal"):
        with st.spinner('Setting your goal...'):
            progress_bar = st.progress(0)
            for percent_complete in range(100):
                time.sleep(0.01)
                progress_bar.progress(percent_complete + 1)
            
            # ✅ Clear the progress bar after completion
            time.sleep(2)  # Wait for 1 second before clearing
            progress_bar.empty()

        start_date = datetime.now()
        end_date = start_date + timedelta(days=duration)
        lesson_plan = [lesson["title"] for lesson in lessons]

        progress["learning_goal"] = {
            "goal_description": goal_description,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "lesson_plan": lesson_plan,
            "completed_lessons": []
        }
        save_json(progress, progress_file)
        st.success(f"🎯 Goal set: **{goal_description}** by **{end_date.strftime('%Y-%m-%d')}**")


# Lessons Section
elif menu == "📚Lesson":
    selected_lesson = st.selectbox("Select a Lesson", [lesson["title"] for lesson in lessons])
    lesson_file = next(lesson["file"] for lesson in lessons if lesson["title"] == selected_lesson)
    lesson = load_json(lesson_file)
    
    # Wrap the lesson content with a styled div
    st.markdown(f"<div class='lesson-card'><h2>{lesson['title']}</h2>", unsafe_allow_html=True)
    for paragraph in lesson["content"]:
        st.markdown(f"<p>{paragraph}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


    if st.button("Mark as Completed"):
        if selected_lesson not in progress["completed_lessons"]:
            progress["completed_lessons"].append(selected_lesson)
            save_json(progress, progress_file)
            st.success(f"'{selected_lesson}' marked as completed!")
        earned_badges = progress.get("earned_badges", [])

    
# Quizzes Section
elif menu == "💡Quiz":
    selected_quiz = st.selectbox("Select a Quiz", [quiz["title"] for quiz in quizzes])
    quiz_file = next(quiz["file"] for quiz in quizzes if quiz["title"] == selected_quiz)
    quiz = load_json(quiz_file)

    # Check if the corresponding lesson is completed
    required_lesson = selected_quiz.lower().replace("quiz: ", "").strip()
    if required_lesson in [lesson.lower() for lesson in progress["completed_lessons"]]:
        st.markdown(f"<div class='quiz-card'>{selected_quiz}</div>", unsafe_allow_html=True)

        user_answers = []
        for question in quiz["questions"]:
            st.write(question["question"])
            options = question["options"]
            user_answers.append(st.radio("Select an answer:", options, key=question["question"]))

        if st.button("Submit Quiz"):
            score = check_answers(quiz["questions"], user_answers)
            st.success(f"Your Score: {score}/{len(quiz['questions'])}")

            progress["quiz_scores"][selected_quiz.lower().replace(" ", "_")] = score
            save_json(progress, progress_file)

            if score == len(quiz["questions"]):
                st.write("Great job! You can move to a higher difficulty level.")
            elif score >= len(quiz["questions"]) // 2:
                st.write("Good work! Keep practicing to improve.")
            else:
                st.write("Don't worry! Review the lesson and try again.")
    else:
        st.warning("Complete the corresponding lesson first.")

elif menu == "📈Progress":
    st.header("Your Learning Progress")
    
    if "learning_goal" in progress and progress["learning_goal"]:
        goal = progress["learning_goal"]
        st.write(f"**Goal**: {goal['goal_description']}")
        st.write(f"**Deadline**: {goal['end_date']}")
        remaining_lessons = [lesson for lesson in goal["lesson_plan"] if lesson not in progress["completed_lessons"]]
        st.write("**Remaining Lessons**:")
        for lesson in remaining_lessons:
            st.write(f"- {lesson}")

        days_left = (datetime.strptime(goal["end_date"], "%Y-%m-%d") - datetime.now()).days
        if days_left < len(remaining_lessons):
            st.warning(f"You are behind schedule! {len(remaining_lessons)} lessons remain, but only {days_left} days left.")
        else:
            st.success(f"You're on track! {len(remaining_lessons)} lessons left in {days_left} days.")
    else:
        st.write("No learning goal set yet.")
    
    # Show streak count with animation
    st.write("### 🔥 Current Learning Streak:")
    live_streak_counter(progress['streak_count'])
    
    # Show badges
    st.write("### 🏆 Earned Badges:")
    if progress['badges']:
        for badge in progress['badges']:
            st.write(f"- {badge}")
    else:
        st.write("No badges earned yet. Keep learning!")

    # Show quiz scores
    st.write("### 📊 Quiz Scores")
    for quiz, score in progress["quiz_scores"].items():
        st.write(f"{quiz}: {score} points")

# Chatbot Section
elif menu == "💬Chatbot":
    st.header("AI Chatbot for Real-Time Q&A in python")
    user_input = st.text_area("Ask your programming-related question here:")
    if st.button("Get Answer"):
        if user_input.strip():
            response = get_hf_response(user_input)
            st.write("**AI Response:**")
            st.write(response)
        else:
            st.warning("Please enter a valid question!")