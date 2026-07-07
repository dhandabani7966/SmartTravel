import streamlit as st
from auth.auth import update_user_password
from utils.validators import check_password_strength
from ui.theme import html_markdown

def show_profile_page():
    """Render the user profile and preferences settings page."""
    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in to view your profile.")
        return
        
    html_markdown(
        """
        <div class="fade-in-up">
            <h1 style="margin-bottom:5px;">User Profile & Settings 👤</h1>
            <p style="color:#5C5C60; font-size:15px; margin-bottom: 25px;">Manage your account credentials, view profile stats, and select app preferences.</p>
        </div>
        """
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Account Details")
        html_markdown(
            f"""
            <div class="glass-card fade-in-up" style="line-height: 1.8;">
                <b>Username:</b> {user['username']} <br>
                <b>Email Address:</b> {user['email']} <br>
                <b>Account Type:</b> {"🛡️ Administrator" if user['is_admin'] else "👤 Standard User"} <br>
                <b>Joined On:</b> {user['created_at']}
            </div>
            """
        )
        
        st.subheader("App Customization")
        # Dark mode toggle
        dark_mode = st.toggle("🌙 Enable Dark Theme Style", value=st.session_state.get("dark_mode", False))
        if dark_mode != st.session_state.get("dark_mode", False):
            st.session_state["dark_mode"] = dark_mode
            st.rerun()
            
        # Log out action
        st.markdown("---")
        if st.button("🚪 Logout from Account", type="primary", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
            st.session_state["is_admin"] = False
            st.session_state["current_page"] = "Home"
            st.toast("Logged out successfully. Good bye!")
            st.rerun()
            
    with col2:
        st.subheader("Change Password")
        
        with st.form("password_change_form"):
            curr_pass = st.text_input("Current Password", type="password")
            new_pass = st.text_input("New Password", type="password")
            confirm_pass = st.text_input("Confirm New Password", type="password")
            
            # Real-time Password Strength Meter
            score, feedback = check_password_strength(new_pass)
            
            # Simple password meter visual
            if new_pass:
                # Color list for meter
                meter_colors = ["#C5221F", "#F4A340", "#B25E00", "#1D7F54"]
                meter_labels = ["Very Weak", "Weak", "Moderate", "Strong"]
                idx = min(score, 3)
                
                # Render meter bar
                width_pct = (score / 4.0) * 100
                html_markdown(
                    f"""
                    <div style="margin-top:10px; margin-bottom:15px; font-family:'Poppins'; font-size:12px;">
                        <span>Password Strength: <b>{meter_labels[idx]}</b></span>
                        <div style="width:100%; height:8px; background:#E2DFD8; border-radius:4px; margin-top:4px; overflow:hidden;">
                            <div style="width:{width_pct}%; height:100%; background:{meter_colors[idx]}; transition:width 0.3s ease;"></div>
                        </div>
                    </div>
                    """
                )
                
                if feedback:
                    for tip in feedback:
                        html_markdown(f"<span style='color:#C5221F; font-size:12px;'>• {tip}</span>")
            
            submit_pass = st.form_submit_button("Update Password 🔑")
            
            if submit_pass:
                if new_pass != confirm_pass:
                    st.error("Passwords do not match.")
                elif score < 3:
                    st.error("Password is too weak. Please address the feedback.")
                else:
                    success, msg = update_user_password(user["id"], curr_pass, new_pass)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
