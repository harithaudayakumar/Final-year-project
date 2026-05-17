import streamlit as st
import numpy as np
import pandas as pd
import os
import pickle
import time
import requests
from pathlib import Path
from streamlit_lottie import st_lottie

st.set_page_config(page_title="Diabetes Risk Prediction", page_icon="🩺", layout="wide")

BASE_DIR = Path(__file__).parent
USERS_FILE = BASE_DIR / "users.csv"
HISTORY_FILE = BASE_DIR / "history.csv"
MODEL_FILE = BASE_DIR / "model.pkl"

model = pickle.load(open(MODEL_FILE, "rb"))

if "page" not in st.session_state:
    st.session_state.page = "login"
if "user" not in st.session_state:
    st.session_state.user = None

def initialize_users_file():
    if not USERS_FILE.exists():
        pd.DataFrame([["admin", "1234"]], columns=["username", "password"]).to_csv(USERS_FILE, index=False)

def load_users():
    initialize_users_file()
    users = pd.read_csv(USERS_FILE, dtype=str)
    users["username"] = users["username"].astype(str).str.strip()
    users["password"] = users["password"].astype(str).str.strip()
    return users

def save_new_user(username, password):
    username = str(username).strip()
    password = str(password).strip()
    users = load_users()

    if username in users["username"].values:
        return False, "Username already exists."

    new_user = pd.DataFrame([[username, password]], columns=["username", "password"])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv(USERS_FILE, index=False)
    return True, "Account created successfully. Please login."

def check_login(username, password):
    username = str(username).strip()
    password = str(password).strip()
    users = load_users()
    return ((users["username"] == username) & (users["password"] == password)).any()

initialize_users_file()

def load_lottie(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        return None
    return None

st.markdown("""
<style>
body { background-color: #f4f6f9; }
.hero {
    padding: 40px;
    border-radius: 15px;
    background: linear-gradient(90deg, #0f2027, #203a43, #2c5364);
    color: white;
    text-align: center;
    margin-bottom: 30px;
}
.card {
    background: white;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}
.stButton>button {
    background-color: #1f77b4;
    color: white;
    height: 50px;
    width: 100%;
    border-radius: 10px;
    font-size: 18px;
    border: none;
}
.stButton>button:hover { background-color: #155d8b; color: white; }
[data-testid="stSidebar"] { background-color: #0f2027; }
[data-testid="stSidebar"] * { color: white; }
</style>
""", unsafe_allow_html=True)

def login():
    st.markdown("""
    <div class="hero">
        <h1>🧠 Diabetes AI Platform</h1>
        <p>Secure Login for Diabetes Risk Prediction System</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🔐 Login")

        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", key="login_button"):
            if check_login(username, password):
                st.session_state.user = username.strip()
                st.session_state.page = "home"
                st.rerun()
            else:
                st.error("Invalid credentials. Please check username/password or create an account.")

        st.markdown("---")

        if st.button("Create New Account", key="go_signup_button"):
            st.session_state.page = "signup"
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

def signup():
    st.markdown("""
    <div class="hero">
        <h1>📝 Create New Account</h1>
        <p>Register as a new user to access the prediction system</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        username = st.text_input("Choose Username", key="signup_username")
        password = st.text_input("Choose Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")

        if st.button("Sign Up", key="signup_button"):
            username = username.strip()
            password = password.strip()
            confirm_password = confirm_password.strip()

            if not username or not password:
                st.warning("Please enter both username and password.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success, message = save_new_user(username, password)
                if success:
                    st.success(message)
                    st.write("Saved username:", username)
                    st.info("Now click Back to Login and login with your new account.")
                else:
                    st.error(message)

        if st.button("Back to Login", key="back_to_login_button"):
            st.session_state.page = "login"
            st.rerun()

        st.caption(f"User file location: {USERS_FILE}")
        st.markdown('</div>', unsafe_allow_html=True)

def home():
    st.markdown("""
    <div class="hero">
        <h1>🩺 Diabetes Risk Prediction System</h1>
        <p>AI-powered health risk assessment tool using Machine Learning</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.3, 1])
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Welcome to the System")
        st.write("""
        This application predicts diabetes risk using a Machine Learning model.
        Users can enter health-related attributes such as glucose level, blood pressure,
        BMI, insulin level, gender, and family history.
        """)
        st.write("✅ User signup/login  ✅ ML prediction  ✅ Dashboard charts  ✅ History tracking")
        if st.button("🚀 Start Prediction", key="start_prediction_button"):
            st.session_state.page = "predict"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        lottie = load_lottie("https://assets2.lottiefiles.com/packages/lf20_jcikwtux.json")
        if lottie:
            st_lottie(lottie, height=300)
        else:
            st.info("Animation could not be loaded. Please check internet connection.")

def predict():
    st.markdown("""
    <div class="hero">
        <h1>🩺 Diabetes Risk Prediction</h1>
        <p>Enter patient details for AI-based diabetes risk analysis</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Enter Patient Details")
        c1, c2 = st.columns(2)

        with c1:
            age = st.number_input("Patient Age", min_value=1, max_value=120, value=30)
            glucose = st.number_input("Glucose Level (mg/dL)", min_value=0.0, max_value=300.0, value=120.0)
            bp = st.number_input("Blood Pressure (mm Hg)", min_value=0.0, max_value=200.0, value=80.0)
            gender = st.selectbox("Gender", ["Male", "Female"])

        with c2:
            insulin = st.number_input("Insulin (mu U/ml)", min_value=0.0, max_value=900.0, value=80.0)
            skin = st.number_input("Skin Thickness (mm)", min_value=0.0, max_value=100.0, value=20.0)
            bmi = st.number_input("BMI", min_value=0.0, max_value=60.0, value=25.0)
            genetics = st.selectbox("Family History / Genetics", ["No", "Yes"])

        predict_btn = st.button("Predict Risk", key="predict_risk_button")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Prediction Result")

        if predict_btn:
            with st.spinner("🧠 AI is analyzing patient data..."):
                time.sleep(2)

            input_data = np.array([[0, glucose, bp, skin, insulin, bmi, 0, age]])
            prediction = model.predict(input_data)[0]
            probability = model.predict_proba(input_data)[0][1]
            risk = int(probability * 100)

            st.progress(risk / 100)
            st.metric("Risk Score", f"{risk}%")

            if prediction == 1:
                st.error("⚠ High Risk of Diabetes")
                result_text = "High Risk"
            else:
                st.success("✅ Low Risk of Diabetes")
                result_text = "Low Risk"

            new_data = pd.DataFrame(
                [[st.session_state.user, age, gender, genetics, glucose, bp, insulin, skin, bmi, risk, result_text]],
                columns=["User", "Age", "Gender", "Genetics", "Glucose", "BP", "Insulin", "Skin", "BMI", "Risk", "Result"]
            )
            new_data.to_csv(HISTORY_FILE, mode="a", header=not HISTORY_FILE.exists(), index=False)
        else:
            st.info("Enter details and click Predict Risk.")

        st.markdown('</div>', unsafe_allow_html=True)

def dashboard():
    st.markdown("""
    <div class="hero">
        <h1>📊 Analytics Dashboard</h1>
        <p>Visual analysis of prediction history</p>
    </div>
    """, unsafe_allow_html=True)

    if not HISTORY_FILE.exists():
        st.info("No prediction data available yet.")
        return

    df = pd.read_csv(HISTORY_FILE)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Predictions", len(df))
    m2.metric("Average Risk", f"{round(df['Risk'].mean(), 2)}%")
    m3.metric("High Risk Cases", len(df[df["Result"] == "High Risk"]))
    m4.metric("Low Risk Cases", len(df[df["Result"] == "Low Risk"]))
    st.markdown('</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Risk Score Trend")
        st.line_chart(df["Risk"])
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Result Distribution")
        st.bar_chart(df["Result"].value_counts())
        st.markdown('</div>', unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Gender-wise Average Risk")
        st.bar_chart(df.groupby("Gender")["Risk"].mean())
        st.markdown('</div>', unsafe_allow_html=True)

    with c4:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Family History Risk")
        st.bar_chart(df.groupby("Genetics")["Risk"].mean())
        st.markdown('</div>', unsafe_allow_html=True)

def history():
    st.markdown("""
    <div class="hero">
        <h1>📋 Prediction History</h1>
        <p>Stored records of previous diabetes risk predictions</p>
    </div>
    """, unsafe_allow_html=True)

    if HISTORY_FILE.exists():
        df = pd.read_csv(HISTORY_FILE)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No records yet.")

def about():
    st.markdown("""
    <div class="hero">
        <h1>ℹ️ About Project</h1>
        <p>Diabetes Prediction Web Application using Machine Learning</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("This final year project predicts diabetes risk using Python, Streamlit, Pandas, NumPy and Scikit-learn.")
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.page not in ["login", "signup"]:
    st.sidebar.markdown("## 🧠 Diabetes AI App")
    st.sidebar.caption(f"Logged in as: {st.session_state.user}")

    page_names = ["Home", "Predict", "Dashboard", "History", "About"]
    page_keys = ["home", "predict", "dashboard", "history", "about"]
    current_index = page_keys.index(st.session_state.page) if st.session_state.page in page_keys else 0

    selected_page = st.sidebar.radio("Navigation", page_names, index=current_index)
    st.session_state.page = page_keys[page_names.index(selected_page)]

    if st.sidebar.button("Logout", key="logout_button"):
        st.session_state.page = "login"
        st.session_state.user = None
        st.rerun()

if st.session_state.page == "login":
    login()
elif st.session_state.page == "signup":
    signup()
elif st.session_state.page == "home":
    home()
elif st.session_state.page == "predict":
    predict()
elif st.session_state.page == "dashboard":
    dashboard()
elif st.session_state.page == "history":
    history()
elif st.session_state.page == "about":
    about()

st.markdown("""
<hr>
<center>
<p style='color:grey'>Final Year Project | Diabetes Prediction App using Machine Learning</p>
</center>
""", unsafe_allow_html=True)
