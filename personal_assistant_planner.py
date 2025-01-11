import openai
import time
from dotenv import load_dotenv
import os
import streamlit as st

# Load .env and OpenAI API key
print("Loading environment variables...")
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print("OpenAI API key loaded successfully.")
    openai.api_key = api_key
else:
    print("Error: OpenAI API key is missing.")
    st.error("OpenAI API key is missing. Please check your .env file.")


# Function to generate the schedule (with improved error handling)
def generate_schedule(tasks, time_frame):
    print("Generating schedule...")
    prompt = f"Create an optimized {time_frame} schedule based on the following tasks:\n"
    for task in tasks:
        prompt += f"- {task}\n"
    prompt += "Please balance productivity and wellness."

    print("Generated prompt:")
    print(prompt)

    max_retries = 3
    retries = 0

    while retries < max_retries:
        try:
            print(f"Attempt {retries + 1} to call OpenAI API...")
            # OpenAI API call to generate schedule
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": prompt}],
                max_tokens=500
            )
            print("OpenAI API call successful.")
            # Extract the response from the model
            schedule = response['choices'][0]['message']['content'].strip()
            print("Generated schedule:")
            print(schedule)
            return schedule
        except openai.error.RateLimitError:
            time.sleep(5)  # Wait 5 seconds before retrying
        except openai.error.AuthenticationError:
            print("Authentication error. Please check your API key.")
            st.error("Authentication error. Please check your API key.")
            return "Authentication error."
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            st.error(f"An unexpected error occurred: {e}")
            return "Error generating schedule."

    print("Failed to generate schedule after multiple retries.")
    return "Failed to generate schedule after multiple retries."


# Streamlit login page
def login_page():
    st.title("Login Page")
    st.write("Please enter your username and password.")

    # Username and password fields
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")


    correct_username = st.secrets["general"]["username"]
    correct_password = st.secrets["general"]["password"]

    if st.button("Login") and username and password:
        if username == correct_username and password == correct_password:
            st.session_state.logged_in = True
            st.success("Login successful!")
        else:
            st.session_state.logged_in = False
            st.error("Invalid username or password. Please try again.")


# Streamlit main app
def main_app():
    st.title("AI Daily Planner")
    st.write("Plan your day or week efficiently with an AI-generated schedule!")

    # User inputs
    time_frame = st.selectbox("Select your planning period:", ["Today", "This Week"])
    tasks_input = st.text_area("Enter your tasks :",
                               placeholder="E.g.\n- Finish report\n- Attend meeting\n- Do yoga")

    # Button to generate the schedule
    if st.button("Generate My Schedule"):
        if tasks_input:
            # Split tasks by new lines
            task_list = tasks_input.strip().split('\n')
            with st.spinner("Generating your schedule..."):
                # Generate the schedule using OpenAI API
                schedule = generate_schedule(task_list, time_frame)
            st.subheader(f"Your Optimized {time_frame} Schedule:")
            st.write(schedule)
        else:
            st.error("Please enter your tasks.")


# Initialize session state for tracking login status
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Show login page if not logged in
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
