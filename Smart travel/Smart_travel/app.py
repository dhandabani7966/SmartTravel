import streamlit as st
import os

# Initial Page Configuration
st.set_page_config(
    page_title="Tamil Nadu Smart Travel Planner",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Imports from custom modules
from utils.logger import setup_logging, get_logger
from database.db import init_db
from auth.auth import ensure_default_admin, authenticate_user, register_user
from ui.theme import inject_theme, html_markdown
from ui.components import render_nav_bar
from ui.animations import render_lottie_hero, render_number_count_up
from utils.validators import validate_email, validate_username, check_password_strength

# Import Pages
from pages.dashboard import show_dashboard
from pages.planner_page import show_planner_page
from pages.history_page import show_history_page
from pages.analytics_page import show_analytics_page
from pages.profile_page import show_profile_page
from pages.admin_page import show_admin_page

# Setup logger
setup_logging()
logger = get_logger("app")

# Initialize database & default accounts
init_db()
ensure_default_admin()

# Initialize Session State Variables
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    st.session_state["is_admin"] = False
    st.session_state["current_page"] = "Home"
    st.session_state["dark_mode"] = False

# Inject premium theme stylesheet
inject_theme()

def show_landing_page():
    """Render the hero landing page for unauthenticated users."""
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        html_markdown(
            """
            <div class="fade-in-up" style="margin-top: 20px;">
                <h1 style="font-size: 42px; line-height: 1.2; font-weight: 800; color: var(--primary);">
                    Explore Tamil Nadu <br> Like Never Before.
                </h1>
                <p style="font-size: 16px; color: #5C5C60; margin: 15px 0 25px 0; line-height: 1.6;">
                    The ultimate Smart Travel Planner tailored exclusively for Tamil Nadu. 
                    Plan day-by-day itineraries, estimate accurate budgets using local baseline data, 
                    track historical trips, and unlock visual travel insights instantly.
                </p>
            </div>
            """
        )
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("🔑 Login to Account", key="hero_login", use_container_width=True):
                st.session_state["current_page"] = "Login"
                st.rerun()
        with btn_col2:
            if st.button("📝 Register Account", key="hero_register", type="primary", use_container_width=True):
                st.session_state["current_page"] = "Register"
                st.rerun()
                
        st.markdown("---")
        st.markdown("### 🎛️ Default Administrator Credentials")
        st.code(
            "Email: admin@smarttravel.local\nPassword: Admin@123",
            language="text"
        )
        st.caption("Use these credentials to view the role-gated admin control panel.")
        
    with right_col:
        # Load and render Lottie Hero animation
        render_lottie_hero()
        
        # Features list card
        html_markdown(
            """
            <div class="glass-card fade-in-up" style="margin-top: 15px;">
                <h4 style="margin-top: 0; color: var(--primary);">💼 Plan with Precision</h4>
                <ul style="padding-left: 20px; font-size: 13px; line-height: 1.8; color: #5C5C60;">
                    <li><b>State-Restricted Database:</b> Tailored lists from Chennai to Kanyakumari.</li>
                    <li><b>Budget Optimizer:</b> Dynamic lodging, food, and transit estimates (2026 data).</li>
                    <li><b>Itinerary Generator:</b> Dynamic day-by-day sightseeing planning.</li>
                    <li><b>History & CSV Export:</b> Save trips and download data in spreadsheet formats.</li>
                    <li><b>Plotly Insights:</b> Cost and destination visualization charts.</li>
                </ul>
            </div>
            """
        )

def show_login_view():
    """Render login form page."""
    html_markdown('<div class="fade-in-up"><h2>Login to Travel Planner</h2></div>')
    
    with st.form("login_form"):
        email_or_user = st.text_input("Username or Email Address")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Authenticate ➔")
        
        if submit:
            if not email_or_user or not password:
                st.error("Please fill in all inputs.")
            else:
                success, user_data, msg = authenticate_user(email_or_user, password)
                if success:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = user_data
                    st.session_state["is_admin"] = user_data["is_admin"]
                    st.session_state["current_page"] = "Home"
                    st.toast("Login successful! Welcome back. 🎉")
                    st.rerun()
                else:
                    st.error(msg)
                    
    if st.button("⬅ Back to Home"):
        st.session_state["current_page"] = "Home"
        st.rerun()

def show_register_view():
    """Render registration form page."""
    html_markdown('<div class="fade-in-up"><h2>Create Account</h2></div>')
    
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        confirm_pass = st.text_input("Confirm Password", type="password")
        
        # Real-time strength check
        score, feedback = check_password_strength(password)
        
        if password:
            meter_colors = ["#C5221F", "#F4A340", "#B25E00", "#1D7F54"]
            meter_labels = ["Very Weak", "Weak", "Moderate", "Strong"]
            idx = min(score, 3)
            width_pct = (score / 4.0) * 100
            
            html_markdown(
                f"""
                <div style="margin-top:10px; margin-bottom:15px; font-size:12px;">
                    <span>Password Strength: <b>{meter_labels[idx]}</b></span>
                    <div style="width:100%; height:6px; background:#E2DFD8; border-radius:3px; margin-top:4px; overflow:hidden;">
                        <div style="width:{width_pct}%; height:100%; background:{meter_colors[idx]};"></div>
                    </div>
                </div>
                """
            )
            
        submit = st.form_submit_button("Create Account ➔")
        
        if submit:
            is_valid_user, user_err = validate_username(username)
            is_valid_email = validate_email(email)
            
            if not is_valid_user:
                st.error(user_err)
            elif not is_valid_email:
                st.error("Please enter a valid email address.")
            elif password != confirm_pass:
                st.error("Passwords do not match.")
            elif score < 3:
                st.error("Password is too weak. Please address strength suggestions.")
            else:
                success, msg = register_user(username, email, password)
                if success:
                    st.success(msg)
                    st.session_state["current_page"] = "Login"
                    st.rerun()
                else:
                    st.error(msg)
                    
    if st.button("⬅ Back to Home"):
        st.session_state["current_page"] = "Home"
        st.rerun()

def show_authenticated_home():
    """Render home dashboard for logged in users."""
    # Greeting Banner
    user = st.session_state["user"]
    html_markdown(
        f"""
        <div class="fade-in-up">
            <h1 style="margin-bottom:5px; color:var(--primary);">Vannakkam, {user['username']}! 🙏</h1>
            <p style="color:#5C5C60; font-size:16px;">Welcome to Tamil Nadu Smart Travel Planner. Let's design your next memorable trip.</p>
        </div>
        """
    )
    
    # Showcase Ooty / Kanyakumari etc.
    st.markdown("### Featured Destinations in Tamil Nadu")
    
    cols = st.columns(3)
    featured = [
        {"name": "Ooty", "region": "Nilgiris (Hill)", "desc": "The Queen of Hill Stations, offering picturesque tea gardens, lakes, and cool weather.", "badge": "Hill Station"},
        {"name": "Mahabalipuram", "region": "Chengalpattu (coastal)", "desc": "Famous 7th-century rock-cut temple carvings and beach view monuments.", "badge": "Heritage & Beach"},
        {"name": "Madurai", "region": "Southern TN", "desc": "Ancient cultural capital surrounding the majestic and historical Meenakshi Temple.", "badge": "Heritage & Temple"}
    ]
    
    for i, item in enumerate(featured):
        with cols[i]:
            html_markdown(
                f"""
                <div class="glass-card fade-in-up">
                    <span style="background-color:#E2F6ED; color:#1D7F54; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:bold;">
                        {item['badge']}
                    </span>
                    <h3 style="margin-top:10px; margin-bottom:5px;">📍 {item['name']}</h3>
                    <p style="font-size:12px; color:#5C5C60; margin-bottom:10px;">{item['region']}</p>
                    <p style="font-size:13px; line-height:1.4;">{item['desc']}</p>
                </div>
                """
            )
            
    html_markdown("<br>")
    if st.button("🗺️ Start Planning A Trip Now", type="primary", use_container_width=True):
        st.session_state["current_page"] = "Plan Trip"
        st.rerun()

# --- MAIN ROUTING LOGIC ---
current_page = st.session_state["current_page"]

# If authenticated, show navigation bar at the top
if st.session_state["authenticated"]:
    render_nav_bar()
    
    if current_page == "Home":
        show_authenticated_home()
    elif current_page == "Plan Trip":
        show_planner_page()
    elif current_page == "History":
        show_history_page()
    elif current_page == "Analytics":
        show_analytics_page()
    elif current_page == "Profile":
        show_profile_page()
    elif current_page == "Admin":
        show_admin_page()
else:
    # Navigation for unauthenticated
    render_nav_bar()
    
    if current_page == "Home":
        show_landing_page()
    elif current_page == "Login":
        show_login_view()
    elif current_page == "Register":
        show_register_view()
