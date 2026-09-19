# app.py - Complete with proper login validation
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import os
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import recommendations module
from recommendations import (
    get_factor_analysis, 
    generate_actionable_recommendations, 
    generate_early_alert,
    get_performance_factors
)

# Page configuration
st.set_page_config(
    page_title="Student Performance Predictor",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6 !important;
        color: #222222 !important;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }

    .metric-card * {
        color: #222222 !important;
    }

    .metric-card h1,
    .metric-card h2,
    .metric-card h3,
    .metric-card h4,
    .metric-card h5,
    .metric-card h6,
    .metric-card p,
    .metric-card span,
    .metric-card li,
    .metric-card strong,
    .metric-card b {
    color: #222222 !important;
}

.risk-high{
        color: #dc3545;
        font-weight: bold;
    }
    .risk-medium {
        color: #fd7e14;
        font-weight: bold;
    }
    .risk-low {
        color: #28a745;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
    }
    .alert-box {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    .login-card {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .credentials-info {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ============ VALID LOGIN CREDENTIALS ============
TEACHER_CREDENTIALS = {
    "admin": "admin123",
    "teacher": "teacher123",
    "professor": "prof123",
    "rizwana": "noor123"
}

# Load the model and data
@st.cache_resource
def load_model():
    """Load the trained model"""
    try:
        model_data = joblib.load('best_model.pkl')
        return model_data
    except FileNotFoundError:
        st.error("Model file not found. Please run model.py first to train the model.")
        return None

@st.cache_data
def load_dataset():
    """Load the student dataset"""
    try:
        df = pd.read_excel('data/student_performance.xlsx', sheet_name='Student Performance')
        return df
    except:
        try:
            df = pd.read_excel('data/student_performance.xlsx', sheet_name='Sheet1')
            return df
        except Exception as e:
            st.error(f"Error loading dataset: {e}")
            return None

@st.cache_data
def load_feature_importance():
    """Load feature importance from saved file"""
    try:
        with open('feature_importance.json', 'r') as f:
            return json.load(f)
    except:
        return []

# Initialize session state for login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = 0

# Helper function to predict student category
def predict_student_performance(student_data, model, scaler, feature_columns):
    """Predict performance category for a student"""
    try:
        features = {}
        for col in feature_columns:
            if col in student_data.index:
                features[col] = student_data[col]
            else:
                features[col] = 0
        
        input_df = pd.DataFrame([features])
        input_df = input_df[feature_columns]
        input_scaled = scaler.transform(input_df)
        prediction = model.predict(input_scaled)[0]
        
        if hasattr(model, 'predict_proba'):
            probs = model.predict_proba(input_scaled)[0]
            return prediction, probs
        return prediction, None
    except Exception as e:
        return "Unknown", None

def get_actual_risk_category(score):
    """Get actual risk category based on Final Exam score"""
    if score < 40:
        return 'At-Risk'
    elif score < 65:
        return 'Average'
    else:
        return 'Good'

# Login page
def login_page():
    if 'teacher_username' not in st.session_state:
        st.session_state.teacher_username = ""

    if 'teacher_password' not in st.session_state:
        st.session_state.teacher_password = ""
       
        def clear_teacher_login():
            st.session_state.teacher_username = ""
            st.session_state.teacher_password = ""
        st.markdown("<h1 class='main-header'>📚 Student Performance Predictor</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='login-card'>", unsafe_allow_html=True)
        st.markdown("<h2 class='sub-header' style='text-align: center;'>Login Portal</h2>", unsafe_allow_html=True)
        
        role = st.selectbox("Select Role", ["Teacher", "Student"])
        
        if role == "Teacher":
            st.markdown("### 👨‍🏫 Teacher Login")
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                key="teacher_username"
)

            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="teacher_password"
)
            def clear_teacher_login():
                st.session_state.teacher_username = ""
                st.session_state.teacher_password = ""

            col_a, col_b = st.columns(2)
            with col_a:
                login_button = st.button("🔐 Login", use_container_width=True)
            with col_b:
                with col_b:
                    st.button(
                        "🗑️ Clear",
                        use_container_width=True,
                        on_click=clear_teacher_login
    )
            
            if login_button:
                if username in TEACHER_CREDENTIALS and TEACHER_CREDENTIALS[username] == password:
                    st.session_state.logged_in = True
                    st.session_state.user_role = "teacher"
                    st.session_state.username = username
                    st.session_state.login_attempts = 0
                    st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    remaining = 3 - st.session_state.login_attempts
                    st.error(f"❌ Invalid username or password! {remaining} attempts remaining.")
                    
                    if st.session_state.login_attempts >= 3:
                        st.error("🔒 Too many failed attempts. Please try again later.")
                        st.stop()
            
            # Show demo credentials
            st.markdown("""
            <div class='credentials-info'>
                <h4>📋 Teacher Demo Credentials:</h4>
                <table style='width: 100%;'>
                    <tr><td><b>Username</b></td><td><b>Password</b></td></tr>
                    <tr><td>admin</td><td>admin123</td></tr>
                    <tr><td>teacher</td><td>teacher123</td></tr>
                    <tr><td>professor</td><td>prof123</td></tr>
                    <tr><td>rizwana</td><td>noor123</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
        
        else:  # Student login
            st.markdown("### 👨‍🎓 Student Login")
            student_id = st.text_input("Student ID", placeholder="Enter your Student ID (e.g., 1, 2, 3...)")
            
            # Show valid student ID range
            df = load_dataset()
            if df is not None:
                min_id = int(df['Student_ID'].min())
                max_id = int(df['Student_ID'].max())
                st.caption(f"💡 Valid Student IDs: {min_id} to {max_id}")
            
            col_a, col_b = st.columns(2)
            with col_a:
                login_button = st.button("🔐 Login as Student", use_container_width=True)
            with col_b:
                if st.button("🗑️ Clear", use_container_width=True):
                    st.rerun()
            
            if login_button:
                if student_id and student_id.isdigit():
                    df = load_dataset()
                    if df is not None:
                        student_id_int = int(student_id)
                        if student_id_int in df['Student_ID'].values:
                            st.session_state.logged_in = True
                            st.session_state.user_role = "student"
                            st.session_state.username = f"Student_{student_id}"
                            st.session_state.student_id = student_id_int
                            st.rerun()
                        else:
                            st.error(f"❌ Student ID {student_id} not found in database!")
                    else:
                        st.error("❌ Unable to load student data. Please check the data file.")
                else:
                    st.error("❌ Please enter a valid numeric Student ID!")
            
            # Show sample student IDs
            if df is not None:
                sample_ids = df['Student_ID'].sample(min(5, len(df))).tolist()
                st.markdown(f"""
                <div class='credentials-info'>
                    <h4>📋 Sample Student IDs:</h4>
                    <code>{', '.join(map(str, sample_ids))}</code>
                    <p style='font-size: 12px; margin-top: 5px;'>Use any ID from {min_id} to {max_id}</p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# Teacher dashboard (using ACTUAL at-risk only - consistent with student view)
def teacher_dashboard(df, model_data):
    st.markdown(f"<h1 class='main-header'>👨‍🏫 Teacher Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>Welcome, <b>{st.session_state.username}</b>! 👋</p>", unsafe_allow_html=True)
    
    model = model_data['model']
    scaler = model_data['scaler']
    feature_columns = model_data['feature_columns']
    
    # Sidebar filters
    st.sidebar.markdown("<h2 class='sub-header'>Filters</h2>", unsafe_allow_html=True)
    
    courses = ['All'] + sorted(df['Course'].unique().tolist())
    selected_course = st.sidebar.selectbox("Select Course", courses)
    
    genders = ['All', 'Male', 'Female']
    selected_gender = st.sidebar.selectbox("Select Gender", genders)

    # ================= STUDENT SEARCH =================
    st.markdown(
        "<h2 class='sub-header'>🔎 Search Student</h2>",
        unsafe_allow_html=True
    )

    col_search, col_button = st.columns([3, 1])

    with col_search:
        search_id = st.text_input(
            "Enter Student ID",
            placeholder="e.g. 121",
            key="teacher_search_id"
        )

    with col_button:
        st.markdown("<br>", unsafe_allow_html=True)
        search_button = st.button(
            "🔍 Search",
            use_container_width=True
        )

    if search_button:
        if search_id and search_id.isdigit():

            search_id_int = int(search_id)

            searched_student = df[
                df['Student_ID'] == search_id_int
            ]

            if not searched_student.empty:

                student = searched_student.iloc[0]

                st.success(
                    f"✅ Student {search_id_int} found!"
                )

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Student ID", student['Student_ID'])

                with col2:
                    st.metric("Course", student['Course'])

                with col3:
                    st.metric(
                        "Attendance",
                        f"{student['Attendance']}%"
                    )

                with col4:
                    st.metric(
                        "Final Exam",
                        student['Final Exam']
                    )

                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric(
                        "Study Hours",
                        student['Study Hours']
                    )

                with col2:
                    st.metric("Gender", student['Gender'])

                with col3:
                    st.metric("Age", student['Age'])

                if student['Final Exam'] < 40:
                    st.error("🔴 At-Risk Student")
                elif student['Final Exam'] < 65:
                    st.warning("🟡 Average Student")
                else:
                    st.success("🟢 Good Student")

                st.markdown("---")

            else:
                st.error(
                    f"❌ Student ID {search_id_int} not found!"
                )

        else:
            st.error(
                "❌ Please enter a valid numeric Student ID!"
            )
    # Apply filters
    filtered_df = df.copy()
    if selected_course != 'All':
        filtered_df = filtered_df[filtered_df['Course'] == selected_course]
    if selected_gender != 'All':
        filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
    
    # Key Metrics
    st.markdown("<h2 class='sub-header'>📊 Key Metrics</h2>", unsafe_allow_html=True)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Total Students", len(filtered_df))
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        avg_attendance = filtered_df['Attendance'].mean()
        st.metric("Avg Attendance", f"{avg_attendance:.1f}%")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        avg_final = filtered_df['Final Exam'].mean()
        st.metric("Avg Final Exam", f"{avg_final:.1f}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        at_risk = len(filtered_df[filtered_df['Final Exam'] < 40])
        st.metric("🔴 At-Risk Students", at_risk, delta=f"{at_risk/len(filtered_df)*100:.1f}% of class" if len(filtered_df)>0 else "0%")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col5:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        excellent = len(filtered_df[filtered_df['Final Exam'] >= 65])
        st.metric("🟢 Excellent Students", excellent, delta=f"{excellent/len(filtered_df)*100:.1f}%" if len(filtered_df)>0 else "0%")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # At-Risk Students Section
    st.markdown("<h2 class='sub-header'>⚠️ At-Risk Students (Final Exam < 40)</h2>", unsafe_allow_html=True)
    
    at_risk_students = filtered_df[filtered_df['Final Exam'] < 40].sort_values('Final Exam')
    
    if len(at_risk_students) > 0:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            risk_display = at_risk_students[['Student_ID', 'Course', 'Attendance', 'Final Exam', 'Study Hours']].copy()
            risk_display.columns = ['Student ID', 'Course', 'Attendance %', 'Final Score', 'Study Hours']
            st.dataframe(risk_display, use_container_width=True)
        
        with col2:
            st.markdown("""
            <div class='metric-card'>
                <h4>🚨 Recommended Actions:</h4>
                <ul>
                    <li>📞 Schedule parent-teacher meeting immediately</li>
                    <li>📖 Provide one-on-one tutoring sessions</li>
                    <li>📅 Monitor daily attendance closely</li>
                    <li>📝 Assign additional practice work</li>
                    <li>📊 Create personalized improvement plan</li>
                    <li>🎯 Set weekly academic goals</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No at-risk students found in the selected filters! Great job!")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3>📈 Performance Distribution</h3>", unsafe_allow_html=True)
        fig = px.histogram(
            filtered_df, 
            x='Final Exam', 
            nbins=20,
            title="Final Exam Score Distribution",
            labels={'Final Exam': 'Score'},
            color_discrete_sequence=['#1E88E5']
        )
        fig.add_vline(x=40, line_dash="dash", line_color="red", annotation_text="At-Risk Threshold")
        fig.add_vline(x=65, line_dash="dash", line_color="green", annotation_text="Good Threshold")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("<h3>📊 Performance by Course</h3>", unsafe_allow_html=True)
        course_perf = filtered_df.groupby('Course')['Final Exam'].agg(['mean', 'count']).reset_index()
        course_perf.columns = ['Course', 'Average Score', 'Student Count']
        
        fig = px.bar(
            course_perf,
            x='Course',
            y='Average Score',
            title="Average Score by Course",
            color='Average Score',
            color_continuous_scale='Viridis',
            text_auto='.1f'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<h3>📉 Attendance vs Final Score</h3>", unsafe_allow_html=True)
        fig = px.scatter(
            filtered_df,
            x='Attendance',
            y='Final Exam',
            color='Course',
            title="Attendance Impact on Performance",
            labels={'Attendance': 'Attendance %', 'Final Exam': 'Final Exam Score'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("<h3>📚 Study Hours vs Performance</h3>", unsafe_allow_html=True)
        filtered_df['Study_Hours_Category'] = pd.cut(
            filtered_df['Study Hours'], 
            bins=[0, 2, 4, 6, 8, 10, 15], 
            labels=['0-2 hrs', '2-4 hrs', '4-6 hrs', '6-8 hrs', '8-10 hrs', '10+ hrs']
        )
        fig = px.box(
            filtered_df,
            x='Study_Hours_Category',
            y='Final Exam',
            title="Study Hours Distribution by Performance",
            labels={'Study_Hours_Category': 'Study Hours Range', 'Final Exam': 'Final Exam Score'},
            color_discrete_sequence=['#1E88E5']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Student List
    st.markdown("<h2 class='sub-header'>📋 Complete Student List</h2>", unsafe_allow_html=True)
    
    display_df = filtered_df[['Student_ID', 'Course', 'Gender', 'Attendance', 'Final Exam', 'Study Hours']].copy()
    display_df['Status'] = display_df['Final Exam'].apply(
        lambda x: '🔴 At-Risk' if x < 40 else ('🟡 Average' if x < 65 else '🟢 Good')
    )
    
    st.dataframe(display_df, use_container_width=True)

# Student dashboard (same as before, works well)
def student_dashboard(df, model_data):
    st.markdown(f"<h1 class='main-header'>👨‍🎓 Student Dashboard</h1>", unsafe_allow_html=True)
    
    student_id = st.session_state.student_id
    student_data = df[df['Student_ID'] == student_id]
    
    if len(student_data) == 0:
        st.error(f"No data found for Student ID: {student_id}")
        return
    
    student = student_data.iloc[0]
    
    model = model_data['model']
    scaler = model_data['scaler']
    feature_columns = model_data['feature_columns']
    feature_importance = model_data.get('feature_importance', [])
    
    predicted_category, _ = predict_student_performance(student, model, scaler, feature_columns)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <h3>Student Information</h3>
            <p><b>Student ID:</b> {student['Student_ID']}</p>
            <p><b>Course:</b> {student['Course']}</p>
            <p><b>Gender:</b> {student['Gender']}</p>
            <p><b>Age:</b> {student['Age']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Attendance", f"{student['Attendance']}%")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Final Exam", f"{student['Final Exam']}")
        if student['Final Exam'] < 40:
            st.markdown("<p class='risk-high'>⚠️ At-Risk</p>", unsafe_allow_html=True)
        elif student['Final Exam'] < 65:
            st.markdown("<p class='risk-medium'>📊 Average</p>", unsafe_allow_html=True)
        else:
            st.markdown("<p class='risk-low'>⭐ Good</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.metric("Study Hours/Week", f"{student['Study Hours']}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col4:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        avg_score = (student['Assignment1'] + student['Assignment2'] + student['Test1'] + student['Test2']) / 4
        st.metric("Avg Assignment/Test", f"{avg_score:.1f}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Performance visualization
    col1, col2 = st.columns(2)
    
    with col1:
        scores = {
            'Assignment 1': student['Assignment1'],
            'Assignment 2': student['Assignment2'],
            'Test 1': student['Test1'],
            'Test 2': student['Test2'],
            'Final Exam': student['Final Exam']
        }
        fig = px.bar(
            x=list(scores.keys()),
            y=list(scores.values()),
            title="Your Performance in Assessments",
            labels={'x': 'Assessment', 'y': 'Score'},
            color=list(scores.values()),
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        progress_data = pd.DataFrame({
            'Assessment': ['Test 1', 'Test 2', 'Final Exam'],
            'Score': [student['Test1'], student['Test2'], student['Final Exam']]
        })
        fig = px.line(
            progress_data,
            x='Assessment',
            y='Score',
            title="Your Progress Over Time",
            markers=True
        )
        fig.update_traces(line_color='#1E88E5', line_width=3)
        st.plotly_chart(fig, use_container_width=True)
    
    # Comparison with class
    same_course = df[df['Course'] == student['Course']]
    
    col1, col2 = st.columns(2)
    
    with col1:
        comparison_data = pd.DataFrame({
            'Category': ['Your Score', 'Class Average'],
            'Score': [student['Final Exam'], same_course['Final Exam'].mean()]
        })
        fig = px.bar(
            comparison_data,
            x='Category',
            y='Score',
            title=f"Comparison with {student['Course']} Class",
            color='Category',
            color_discrete_sequence=['#1E88E5', '#FFC107']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        percentile = (same_course['Final Exam'] < student['Final Exam']).sum() / len(same_course) * 100
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=percentile,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Percentile in {student['Course']} Class"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#1E88E5"},
                'steps': [
                    {'range': [0, 25], 'color': "red"},
                    {'range': [25, 50], 'color': "orange"},
                    {'range': [50, 75], 'color': "yellow"},
                    {'range': [75, 100], 'color': "green"}
                ]
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.markdown("<h2 class='sub-header'>💡 Recommendations</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("### 📚 Study Habits")
        if student['Study Hours'] < 4:
            st.warning("⚠️ Increase study hours")
            st.markdown("• Aim for 6-8 hours/week")
            st.markdown("• Create a study schedule")
        else:
            st.success("✅ Good study habits!")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("### 📝 Attendance")
        if student['Attendance'] < 75:
            st.warning("⚠️ Improve attendance")
            st.markdown("• Aim for 85%+ attendance")
        else:
            st.success("✅ Good attendance!")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
        st.markdown("### 🎯 Focus Areas")
        if student['Final Exam'] < 40:
            st.error("🔴 Critical: Need immediate action")
            st.markdown("• Meet with teacher")
            st.markdown("• Extra tutoring required")
        elif student['Final Exam'] < 65:
            st.warning("🟡 Room for improvement")
            st.markdown("• Focus on weak topics")
            st.markdown("• Practice more")
        else:
            st.success("🟢 Keep up the good work!")
        st.markdown("</div>", unsafe_allow_html=True)

# Main app
def main():
    model_data = load_model()
    df = load_dataset()
    
    if model_data is None or df is None:
        st.error("Please make sure:")
        st.info("1. Run 'python model.py' first to train the model")
        st.info("2. Ensure 'data/student_performance.xlsx' exists")
        return
    
    if not st.session_state.logged_in:
        login_page()
    else:
        with st.sidebar:
            st.markdown(f"### 👤 Logged in as")
            st.markdown(f"**{st.session_state.user_role.title()}:** {st.session_state.username}")
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.user_role = None
                st.session_state.username = None
                if 'student_id' in st.session_state:
                    del st.session_state.student_id
                st.rerun()
            
            st.markdown("---")
            st.markdown("### 📌 About")
            st.markdown("""
            This system predicts student performance and provides:
            - 📊 Real-time analytics
            - 🚨 Early risk alerts
            - 💡 Personalized recommendations
            - 📈 Progress tracking
            """)
        
        if st.session_state.user_role == "teacher":
            teacher_dashboard(df, model_data)
        else:
            student_dashboard(df, model_data)

if __name__ == "__main__":
    main()