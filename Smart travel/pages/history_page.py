import streamlit as st
import pandas as pd
from services.planner import get_user_trips, delete_trip
from ui.components import render_budget_badge
from ui.theme import html_markdown

def show_history_page():
    """Render the trip history page."""
    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in to view your trip history.")
        return
        
    st.markdown(
        """
        <div class="fade-in-up">
            <h1 style="margin-bottom:5px;">Your Planned Journeys 📜</h1>
            <p style="color:#5C5C60; font-size:15px; margin-bottom: 25px;">Search, export, or manage your saved Tamil Nadu trip itineraries.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    trips = get_user_trips(user["id"])
    
    if not trips:
        st.info("You haven't saved any trips yet. Head over to the Planner page to create your first itinerary!")
        if st.button("🗺️ Start Planning Now", type="primary"):
            st.session_state["current_page"] = "Plan Trip"
            st.rerun()
        return
        
    # Search and filter
    search_query = st.text_input("🔍 Search by Destination", "").strip().lower()
    
    filtered_trips = trips
    if search_query:
        filtered_trips = [t for t in trips if search_query in t["destination"].lower()]
        
    # CSV Export Setup
    if filtered_trips:
        df = pd.DataFrame(filtered_trips)
        # Clean up dataframe for user presentation
        df_export = df.rename(columns={
            "destination": "Destination",
            "days": "Duration (Days)",
            "budget": "Budget Limit (INR)",
            "travelers": "Travelers Count",
            "travel_type": "Travel Type",
            "transport_mode": "Transport Mode",
            "hotel_category": "Hotel Class",
            "estimated_cost": "Estimated Cost (INR)",
            "budget_status": "Budget Status",
            "created_at": "Saved At"
        })
        
        # Drop id column if present
        if "id" in df_export.columns:
            df_export = df_export.drop(columns=["id"])
            
        csv_data = df_export.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            label="📥 Export Search Results to CSV",
            data=csv_data,
            file_name="tamilnadu_trip_history.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    st.markdown("---")
    
    if not filtered_trips:
        st.warning("No trips matched your search query.")
        return
        
    for trip in filtered_trips:
        badge_html = render_budget_badge(trip["budget_status"])
        
        with st.container():
            html_markdown(
                f"""
                <div class="glass-card fade-in-up">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <h3 style="margin:0;">📍 {trip['destination']}</h3>
                        {badge_html}
                    </div>
                    <div style="font-size:14px; color:#5C5C60; line-height:1.6; margin-bottom:15px;">
                        <b>Trip Duration:</b> {trip['days']} Days <br>
                        <b>Travelers:</b> {trip['travelers']} ({trip['travel_type']}) <br>
                        <b>Transport:</b> {trip['transport_mode']} | <b>Hotel Class:</b> {trip['hotel_category']} <br>
                        <b>Budget Limit:</b> ₹{int(trip['budget']):,} | <b>Estimated Total Cost:</b> ₹{int(trip['estimated_cost']):,} <br>
                        <span style="font-size:11px; color:#A0AAB2;">Created on: {trip['created_at']}</span>
                    </div>
                </div>
                """
            )
            
            # Action button row (Streamlit buttons outside the HTML markup to capture state)
            col1, col2 = st.columns([4, 1])
            with col2:
                # Unique key for button
                if st.button("🗑️ Delete Trip", key=f"del_trip_{trip['id']}", type="secondary"):
                    if delete_trip(trip["id"], user["id"]):
                        st.toast(f"Trip to {trip['destination']} deleted.")
                        st.rerun()
                    else:
                        st.error("Failed to delete trip.")
                        
            st.markdown("<br>", unsafe_allow_html=True)
