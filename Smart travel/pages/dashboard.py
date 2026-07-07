import streamlit as st
from services.planner import get_user_trips
from ui.components import render_budget_badge
from ui.theme import html_markdown

def show_dashboard():
    """Render the dashboard page."""
    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in to view your dashboard.")
        return
        
    html_markdown(
        f"""
        <div class="fade-in-up">
            <h1 style="margin-bottom:0;">Welcome back, {user['username']}! 👋</h1>
            <p style="color:#5C5C60; font-size:16px;">Here is an overview of your travel planning activities.</p>
        </div>
        """
    )
    
    # Load user trips
    trips = get_user_trips(user["id"])
    
    # Calculate stats
    total_trips = len(trips)
    total_budget = sum([t["budget"] for t in trips])
    avg_days = sum([t["days"] for t in trips]) / total_trips if total_trips > 0 else 0
    
    # Draw stats metric cards
    cols = st.columns(3)
    with cols[0]:
        html_markdown(
            f"""
            <div class="glass-card fade-in-up" style="text-align: center;">
                <div style="font-size: 14px; font-weight: 500; color: #5C5C60;">Trips Planned</div>
                <div style="font-size: 32px; font-weight: 700; color: var(--primary); margin-top: 10px;">{total_trips}</div>
            </div>
            """
        )
    with cols[1]:
        html_markdown(
            f"""
            <div class="glass-card fade-in-up" style="text-align: center;">
                <div style="font-size: 14px; font-weight: 500; color: #5C5C60;">Total Budget Allocated</div>
                <div style="font-size: 32px; font-weight: 700; color: var(--primary); margin-top: 10px;">₹{int(total_budget):,}</div>
            </div>
            """
        )
    with cols[2]:
        html_markdown(
            f"""
            <div class="glass-card fade-in-up" style="text-align: center;">
                <div style="font-size: 14px; font-weight: 500; color: #5C5C60;">Avg. Trip Duration</div>
                <div style="font-size: 32px; font-weight: 700; color: var(--primary); margin-top: 10px;">{avg_days:.1f} days</div>
            </div>
            """
        )
        
    st.markdown("---")
    
    left_col, right_col = st.columns([2, 1])
    
    with left_col:
        st.subheader("Your Recent Trips")
        if total_trips == 0:
            st.info("You haven't planned any trips yet! Get started by clicking 'Plan Trip' in the menu.")
            if st.button("🗺️ Plan My First Trip", type="primary"):
                st.session_state["current_page"] = "Plan Trip"
                st.rerun()
        else:
            for trip in trips[:3]:
                badge = render_budget_badge(trip['budget_status'])
                html_markdown(
                    f"""
                    <div class="glass-card fade-in-up">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h3 style="margin:0;">📍 {trip['destination']}</h3>
                            {badge}
                        </div>
                        <div style="margin-top:10px; font-size:14px; color:#5C5C60;">
                            <b>Duration:</b> {trip['days']} days | <b>Travelers:</b> {trip['travelers']} | <b>Type:</b> {trip['travel_type']}
                        </div>
                        <div style="margin-top:8px; font-size:14px; color:#5C5C60;">
                            <b>Budget:</b> ₹{int(trip['budget']):,} | <b>Est. Cost:</b> ₹{int(trip['estimated_cost']):,}
                        </div>
                    </div>
                    """
                )
            if total_trips > 3:
                if st.button("📜 View All Trips History"):
                    st.session_state["current_page"] = "History"
                    st.rerun()
                    
    with right_col:
        st.subheader("Quick Actions")
        html_markdown(
            """
            <div class="glass-card fade-in-up" style="padding:15px;">
                <h4 style="margin-top:0;">Need Inspiration?</h4>
                <p style="font-size:13px; color:#5C5C60; line-height:1.4;">
                    Check out the top-ranked travel spots in Tamil Nadu based on real-time budget ranges.
                </p>
            </div>
            """
        )
        if st.button("Plan Trip 🗺️", use_container_width=True, type="primary"):
            st.session_state["current_page"] = "Plan Trip"
            st.rerun()
        if st.button("View Analytics 📊", use_container_width=True):
            st.session_state["current_page"] = "Analytics"
            st.rerun()
        if st.button("Manage Profile 👤", use_container_width=True):
            st.session_state["current_page"] = "Profile"
            st.rerun()
