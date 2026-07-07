import streamlit as st
import pandas as pd
import plotly.express as px
from services.planner import get_user_trips
from utils.logger import get_logger
from ui.theme import get_theme_colors

logger = get_logger("analytics_page")

def show_analytics_page():
    """Render the Plotly analytics page."""
    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in to view your analytics.")
        return
        
    st.markdown(
        """
        <div class="fade-in-up">
            <h1 style="margin-bottom:5px;">Travel Insights & Analytics 📊</h1>
            <p style="color:#5C5C60; font-size:15px; margin-bottom: 25px;">Visualizing your travel stats, cost estimations, and budget limits.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    trips = get_user_trips(user["id"])
    
    if not trips:
        st.info("You haven't planned any trips yet. Add some trips using the Planner to generate visual graphs!")
        return
        
    df = pd.DataFrame(trips)
    
    # Overview Cards
    total_trips = len(df)
    total_budget = df["budget"].sum()
    total_est_cost = df["estimated_cost"].sum()
    avg_travelers = df["travelers"].mean()
    
    st.markdown("### Executive Summary")
    
    cols = st.columns(4)
    with cols[0]:
        st.markdown(f'<div class="glass-card" style="text-align:center; padding:10px;"><div style="font-size:12px; color:#5C5C60;">Total Trips</div><div style="font-size:24px; font-weight:700; color:var(--primary);">{total_trips}</div></div>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown(f'<div class="glass-card" style="text-align:center; padding:10px;"><div style="font-size:12px; color:#5C5C60;">Total Budget</div><div style="font-size:24px; font-weight:700; color:var(--primary);">₹{int(total_budget):,}</div></div>', unsafe_allow_html=True)
    with cols[2]:
        st.markdown(f'<div class="glass-card" style="text-align:center; padding:10px;"><div style="font-size:12px; color:#5C5C60;">Total Est. Cost</div><div style="font-size:24px; font-weight:700; color:var(--primary);">₹{int(total_est_cost):,}</div></div>', unsafe_allow_html=True)
    with cols[3]:
        st.markdown(f'<div class="glass-card" style="text-align:center; padding:10px;"><div style="font-size:12px; color:#5C5C60;">Avg. Travelers</div><div style="font-size:24px; font-weight:700; color:var(--primary);">{avg_travelers:.1f}</div></div>', unsafe_allow_html=True)
        
    st.markdown("---")
    
    # 1. Pie Chart: Destination Share
    st.markdown("### Destination Popularity Share")
    dest_counts = df["destination"].value_counts().reset_index()
    dest_counts.columns = ["Destination", "Count"]
    
    fig_pie = px.pie(
        dest_counts, 
        values="Count", 
        names="Destination",
        color_discrete_sequence=px.colors.qualitative.Prism,
        hole=0.4
    )
    fig_pie.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Poppins, Inter, sans-serif", size=12),
        margin=dict(t=10, b=10, l=10, r=10)
    )
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # 2. Bar Chart: Budget limit vs. Estimated Cost per Destination
    st.markdown("### Cost Comparison per Destination")
    avg_costs = df.groupby("destination")[["budget", "estimated_cost"]].mean().reset_index()
    avg_costs.columns = ["Destination", "Avg. Budget Limit", "Avg. Estimated Cost"]
    
    df_melt = pd.melt(
        avg_costs, 
        id_vars=["Destination"], 
        value_vars=["Avg. Budget Limit", "Avg. Estimated Cost"],
        var_name="Category", 
        value_name="Amount (₹)"
    )
    
    colors = get_theme_colors()
    fig_bar = px.bar(
        df_melt, 
        x="Destination", 
        y="Amount (₹)", 
        color="Category",
        barmode="group",
        color_discrete_map={
            "Avg. Budget Limit": colors["accent"],
            "Avg. Estimated Cost": colors["primary"]
        }
    )
    fig_bar.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Poppins, Inter, sans-serif", size=12),
        xaxis_title="Destination",
        yaxis_title="Amount (₹)",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # 3. Bar Chart: Budget status distribution
    st.markdown("### Budget status breakdown")
    status_counts = df["budget_status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Count"]
    
    fig_status = px.bar(
        status_counts,
        x="Status",
        y="Count",
        color="Status",
        color_discrete_map={
            "Within Budget": "#1D7F54",
            "Near Limit": "#B25E00",
            "Exceeded": "#C5221F"
        }
    )
    fig_status.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Poppins, Inter, sans-serif", size=12),
        showlegend=False
    )
    st.plotly_chart(fig_status, use_container_width=True)
