import streamlit as st
import json
from services.recommendation_engine import recommend_destinations
from services.budget_engine import calculate_trip_budget
from services.itinerary_generator import generate_itinerary
from services.planner import save_trip
from ui.components import render_destination_card, render_budget_badge
from ui.animations import render_number_count_up, render_loading_shimmer
from ui.theme import html_markdown, get_theme_colors

def render_step_indicator(step: int):
    """Render a premium step progress bar."""
    steps = ["Configure", "Select Destination", "Preferences", "Review & Save"]
    progress_percent = int(((step - 1) / (len(steps) - 1)) * 100)
    colors = get_theme_colors()
    
    html = f"""
    <div style="margin-bottom: 35px; font-family: 'Poppins', sans-serif;">
        <div style="position: relative; display: flex; justify-content: space-between; align-items: center; width: 100%;">
            <!-- Progress Line -->
            <div style="position: absolute; top: 15px; left: 0; right: 0; height: 4px; background: {colors['border']}; z-index: 1;"></div>
            <div style="position: absolute; top: 15px; left: 0; width: {progress_percent}%; height: 4px; background: {colors['primary']}; z-index: 2; transition: width 0.4s ease;"></div>
            
            <!-- Step Items -->
    """
    
    for i, name in enumerate(steps):
        step_num = i + 1
        is_completed = step_num < step
        is_active = step_num == step
        
        bg_color = colors["primary"] if (is_completed or is_active) else colors["sidebar_bg"]
        border_color = colors["primary"] if (is_completed or is_active) else colors["border"]
        text_color = "white" if (is_completed or is_active) else colors["text_muted"]
        font_weight = "bold" if is_active else "normal"
        
        html += f"""
        <div style="z-index: 3; text-align: center; display: flex; flex-direction: column; align-items: center;">
            <div style="width: 32px; height: 32px; border-radius: 50%; background: {bg_color}; border: 2px solid {border_color}; color: {text_color}; display: flex; justify-content: center; align-items: center; font-size: 14px; font-weight: bold;">
                {step_num}
            </div>
            <span style="font-size: 12px; margin-top: 8px; color: { colors['text'] if is_active else colors['text_muted'] }; font-weight: {font_weight};">
                {name}
            </span>
        </div>
        """
        
    html += """
        </div>
    </div>
    """
    html_markdown(html)

def show_planner_page():
    """Render the multi-step trip planner page."""
    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in to plan a trip.")
        return
        
    # Init planner session states
    if "planner_step" not in st.session_state:
        st.session_state["planner_step"] = 1
        st.session_state["p_budget"] = 15000.0
        st.session_state["p_days"] = 3
        st.session_state["p_travelers"] = 2
        st.session_state["p_travel_type"] = "Family"
        st.session_state["p_include_pondicherry"] = True
        st.session_state["p_selected_destination"] = None
        st.session_state["p_hotel_category"] = "Mid-range"
        st.session_state["p_food_category"] = "Mid-range"
        st.session_state["p_transport_mode"] = "Train (Sleeper/3AC)"

    step = st.session_state["planner_step"]
    
    st.markdown(
        """
        <div class="fade-in-up">
            <h1 style="margin-bottom: 5px;">Plan Your Tamil Nadu Journey 🗺️</h1>
            <p style="color:#5C5C60; font-size:15px; margin-bottom: 25px;">Enter details, get state-restricted smart recommendations, customize details, and generate itineraries.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    render_step_indicator(step)
    
    # ------------------ STEP 1: CONFIGURE INPUTS ------------------
    if step == 1:
        st.subheader("Step 1: Where and how are you traveling?")
        
        with st.form("inputs_form"):
            budget = st.number_input("Total Trip Budget (₹)", min_value=1000.0, max_value=1000000.0, value=st.session_state["p_budget"], step=1000.0)
            days = st.number_input("Number of Days", min_value=1, max_value=30, value=st.session_state["p_days"])
            travelers = st.number_input("Number of Travelers", min_value=1, max_value=100, value=st.session_state["p_travelers"])
            
            travel_type = st.selectbox(
                "Travel Type",
                ["Solo", "Family", "Friends", "Business"],
                index=["Solo", "Family", "Friends", "Business"].index(st.session_state["p_travel_type"])
            )
            
            include_pondicherry = st.checkbox(
                "Include Pondicherry (Nearby UT - Outside TN)", 
                value=st.session_state["p_include_pondicherry"]
            )
            
            submit_inputs = st.form_submit_button("Find Recommendations ➔")
            
            if submit_inputs:
                st.session_state["p_budget"] = budget
                st.session_state["p_days"] = days
                st.session_state["p_travelers"] = travelers
                st.session_state["p_travel_type"] = travel_type
                st.session_state["p_include_pondicherry"] = include_pondicherry
                st.session_state["planner_step"] = 2
                st.rerun()

    # ------------------ STEP 2: SELECT RECOMMENDATION ------------------
    elif step == 2:
        st.subheader("Step 2: Choose your Destination")
        
        # Load recommendations
        recs = recommend_destinations(
            budget_limit=st.session_state["p_budget"],
            days=st.session_state["p_days"],
            travelers=st.session_state["p_travelers"],
            travel_type=st.session_state["p_travel_type"],
            include_pondicherry=st.session_state["p_include_pondicherry"]
        )
        
        if not recs:
            st.error("No Tamil Nadu destinations match your budget limits. Try increasing your budget or reducing the number of travelers/days.")
            if st.button("⬅ Go Back"):
                st.session_state["planner_step"] = 1
                st.rerun()
            return
            
        st.info("Here are custom destinations matching your criteria. Select one to proceed.")
        
        # Render cards
        for rec in recs:
            render_destination_card(rec, rec["attractions"])
            
        # Selectbox to finalize
        names = [r["name"] for r in recs]
        selected = st.selectbox("Select Destination", names)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅ Back to Inputs"):
                st.session_state["planner_step"] = 1
                st.rerun()
        with col2:
            if st.button("Proceed to Options ➔"):
                st.session_state["p_selected_destination"] = selected
                st.session_state["planner_step"] = 3
                st.rerun()

    # ------------------ STEP 3: PREFERENCES & LOGISTICS ------------------
    elif step == 3:
        st.subheader(f"Step 3: Customize logistics for {st.session_state['p_selected_destination']}")
        
        hotel_opts = ["Budget", "Mid-range", "Premium", "Luxury"]
        food_opts = ["Budget", "Mid-range", "Premium"]
        transport_opts = [
            "TNSTC/private bus", 
            "Train (Sleeper/3AC)", 
            "Flight (intra-TN/metro hop)", 
            "Rental car with driver", 
            "Self-drive cab"
        ]
        
        with st.form("preferences_form"):
            hotel = st.selectbox("Hotel Standard", hotel_opts, index=hotel_opts.index(st.session_state["p_hotel_category"]))
            food = st.selectbox("Food Budget Standard", food_opts, index=food_opts.index(st.session_state["p_food_category"]))
            transport = st.selectbox("Transportation Mode", transport_opts, index=transport_opts.index(st.session_state["p_transport_mode"]))
            
            submit_prefs = st.form_submit_button("Generate Itinerary & Budget Review ➔")
            if submit_prefs:
                st.session_state["p_hotel_category"] = hotel
                st.session_state["p_food_category"] = food
                st.session_state["p_transport_mode"] = transport
                st.session_state["planner_step"] = 4
                st.rerun()
                
        if st.button("⬅ Back to Destinations"):
            st.session_state["planner_step"] = 2
            st.rerun()

    # ------------------ STEP 4: REVIEW & SAVE ------------------
    elif step == 4:
        st.subheader("Step 4: Final Review & Itinerary")
        
        # Load distance from Chennai
        dest_name = st.session_state["p_selected_destination"]
        
        # Fetch distance
        from database.db import fetch_one
        dest_data = fetch_one("SELECT distance_from_chennai_km FROM destinations WHERE name = ?", (dest_name,))
        distance = dest_data["distance_from_chennai_km"] if dest_data else 0
        
        # Budget math
        breakdown, status = calculate_trip_budget(
            destination_name=dest_name,
            distance_km=distance,
            days=st.session_state["p_days"],
            travelers=st.session_state["p_travelers"],
            travel_type=st.session_state["p_travel_type"],
            transport_mode=st.session_state["p_transport_mode"],
            hotel_category=st.session_state["p_hotel_category"],
            food_category=st.session_state["p_food_category"],
            budget_limit=st.session_state["p_budget"]
        )
        
        # Render budget badge & count-up animation
        badge_html = render_budget_badge(status)
        html_markdown(
            f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                <h4 style="margin:0;">Budget Status</h4>
                {badge_html}
            </div>
            """
        )
        
        render_number_count_up(breakdown["total_cost"])
        
        # Details breakdown table
        html_markdown(
            f"""
            <div class="glass-card">
                <h4 style="margin-top:0;">Cost Breakdown</h4>
                <table style="width:100%; font-size:14px; border-collapse:collapse;">
                    <tr style="border-bottom:1px solid #E2DFD8; padding:8px 0;">
                        <td style="padding:8px 0;">🏨 <b>Hotel Lodging:</b></td>
                        <td style="text-align:right;">₹{int(breakdown['hotel_cost']):,}</td>
                    </tr>
                    <tr style="border-bottom:1px solid #E2DFD8;">
                        <td style="padding:8px 0;">🍔 <b>Food Expenses:</b></td>
                        <td style="text-align:right;">₹{int(breakdown['food_cost']):,}</td>
                    </tr>
                    <tr style="border-bottom:1px solid var(--border);">
                        <td style="padding:8px 0;">🚗 <b>Transportation:</b></td>
                        <td style="text-align:right;">₹{int(breakdown['transport_cost']):,}</td>
                    </tr>
                    <tr style="border-bottom:1px solid var(--border);">
                        <td style="padding:8px 0;">🛡️ <b>Miscellaneous Buffer:</b></td>
                        <td style="text-align:right;">₹{int(breakdown['buffer_cost']):,}</td>
                    </tr>
                    <tr style="font-weight:bold; font-size:16px;">
                        <td style="padding:10px 0; color:var(--primary);">Total Estimated Cost:</td>
                        <td style="text-align:right; color:var(--primary);">₹{int(breakdown['total_cost']):,}</td>
                    </tr>
                </table>
            </div>
            """
        )
        
        # Itinerary preview
        st.subheader("Day-by-Day Itinerary Preview")
        itinerary = generate_itinerary(dest_name, st.session_state["p_days"])
        
        for item in itinerary:
            html_markdown(
                f"""
                <div class="glass-card">
                    <h4 style="margin-top:0; color:var(--primary);">☀️ Day {item['day']}</h4>
                    <p style="margin-bottom:10px; font-size:14px;"><b>Morning:</b> {item['morning']}</p>
                    <p style="margin-bottom:10px; font-size:14px;"><b>Afternoon:</b> {item['afternoon']}</p>
                    <p style="margin-bottom:10px; font-size:14px;"><b>Evening:</b> {item['evening']}</p>
                    <div style="font-size:12px; color:#A0AAB2; border-top:1px dashed var(--border); padding-top:8px; margin-top:8px;">
                        💡 <b>Travel Tip:</b> {item['notes']}
                    </div>
                </div>
                """
            )
            
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅ Adjust Logistics"):
                st.session_state["planner_step"] = 3
                st.rerun()
        with col2:
            if st.button("💾 Save Trip to History"):
                # Save to database
                save_trip(
                    user_id=user["id"],
                    destination=dest_name,
                    days=st.session_state["p_days"],
                    budget=st.session_state["p_budget"],
                    travelers=st.session_state["p_travelers"],
                    travel_type=st.session_state["p_travel_type"],
                    transport_mode=st.session_state["p_transport_mode"],
                    hotel_category=st.session_state["p_hotel_category"],
                    estimated_cost=breakdown["total_cost"],
                    budget_status=status
                )
                st.toast("Trip saved successfully! 🎉")
                
                # Clear session state
                st.session_state["planner_step"] = 1
                st.session_state["current_page"] = "History"
                st.rerun()
