import streamlit as st
from typing import Dict, Any, List
from ui.theme import html_markdown

def render_nav_bar():
    """Render a premium top navigation bar."""
    authenticated = st.session_state.get("authenticated", False)
    is_admin = st.session_state.get("is_admin", False)
    
    # Base pages list
    if not authenticated:
        pages = ["Home", "Login", "Register"]
    else:
        pages = ["Home", "Plan Trip", "History", "Analytics", "Profile"]
        if is_admin:
            pages.append("Admin")
            
    # CSS container injection
    st.markdown('<div class="custom-nav-container">', unsafe_allow_html=True)
    
    # Create columns matching number of pages
    cols = st.columns(len(pages))
    
    current_page = st.session_state.get("current_page", "Home")
    
    for i, page in enumerate(pages):
        with cols[i]:
            icon = ""
            if page == "Home": icon = "🏠 "
            elif page == "Plan Trip": icon = "🗺️ "
            elif page == "History": icon = "📜 "
            elif page == "Analytics": icon = "📊 "
            elif page == "Profile": icon = "👤 "
            elif page == "Admin": icon = "🛡️ "
            elif page == "Login": icon = "🔑 "
            elif page == "Register": icon = "📝 "
            
            is_active = (current_page == page)
            
            # Using primary styling for active, secondary for others
            btn_type = "primary" if is_active else "secondary"
            
            if st.button(f"{icon}{page}", key=f"nav_btn_{page}", type=btn_type, use_container_width=True):
                st.session_state["current_page"] = page
                st.rerun()
                
    st.markdown('</div>', unsafe_allow_html=True)

def render_destination_card(dest: Dict[str, Any], attractions: List[str]):
    """Render a glassmorphism travel card for destinations."""
    ut_badge = ""
    if dest.get("is_ut"):
        ut_badge = "<span style='background-color:#F4A340; color:white; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:bold; margin-left:10px;'>UT - Nearby</span>"
        
    attr_list_html = "".join([f"<li style='margin-bottom: 4px;'>{attr}</li>" for attr in attractions[:3]])
    
    card_html = f"""
    <div class="glass-card fade-in-up">
        <h3 style="margin-top: 0; display:flex; align-items:center;">
            📍 {dest['name']} {ut_badge}
        </h3>
        <p style="font-size:12px; font-weight:600; color:var(--primary); text-transform:uppercase; margin-bottom:10px;">
            Region: {dest['region']} | Best Season: {dest['best_season']}
        </p>
        <p style="margin-bottom:15px; font-size:14px; line-height:1.5;">
            {dest['description']}
        </p>
        <div style="font-size: 13px; font-weight: 500; margin-bottom: 5px;">Key Attractions:</div>
        <ul style="padding-left:20px; font-size:13px; color:#5C5C60; margin-bottom:15px;">
            {attr_list_html}
        </ul>
        <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border); padding-top:10px; margin-top:10px; font-size:13px;">
            <span>Distance: <b>{dest['distance_from_chennai_km']} km</b> from Chennai</span>
            <span>Est. Base Cost: <b>₹{int(dest['estimated_base_cost']):,}</b></span>
        </div>
    </div>
    """
    html_markdown(card_html)

def render_budget_badge(status: str):
    """Render a colored budget badge."""
    if status == "Within Budget":
        bg, text = "#E2F6ED", "#1D7F54"
    elif status == "Near Limit":
        bg, text = "#FFF4E5", "#B25E00"
    else:
        bg, text = "#FCE8E6", "#C5221F"
        
    return f'<span style="background-color: {bg}; color: {text}; padding: 6px 12px; border-radius: 12px; font-size: 13px; font-weight: 600; display: inline-block; white-space: nowrap;">{status}</span>'

