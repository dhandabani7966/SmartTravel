import streamlit as st
import pandas as pd
from database.db import fetch_all, execute, log_audit
from services.planner import get_all_trips, delete_trip
from utils.logger import get_logger
from ui.theme import html_markdown

logger = get_logger("admin_page")

def show_admin_page():
    """Render the admin panel (role-gated)."""
    user = st.session_state.get("user")
    is_admin = st.session_state.get("is_admin", False)
    
    # Gating check
    if not user or not is_admin:
        st.error("🔒 Access Denied. This panel is restricted to administrators.")
        return
        
    html_markdown(
        """
        <div class="fade-in-up">
            <h1 style="margin-bottom:5px;">System Administrator Panel 🛡️</h1>
            <p style="color:#5C5C60; font-size:15px; margin-bottom: 25px;">Platform audit logging, user credentials management, and overall trip coordination dashboard.</p>
        </div>
        """
    )
    
    # 1. Fetch statistics
    user_count = fetch_one_val("SELECT COUNT(*) as count FROM users")
    trip_count = fetch_one_val("SELECT COUNT(*) as count FROM trips")
    total_est_cost = fetch_one_val("SELECT SUM(estimated_cost) as total FROM trips") or 0.0
    
    cols = st.columns(3)
    with cols[0]:
        html_markdown(f'<div class="glass-card" style="text-align:center;"><div style="font-size:12px; color:#5C5C60;">Total Registered Users</div><div style="font-size:28px; font-weight:700; color:var(--primary);">{user_count}</div></div>')
    with cols[1]:
        html_markdown(f'<div class="glass-card" style="text-align:center;"><div style="font-size:12px; color:#5C5C60;">Total Trips Planned</div><div style="font-size:28px; font-weight:700; color:var(--primary);">{trip_count}</div></div>')
    with cols[2]:
        html_markdown(f'<div class="glass-card" style="text-align:center;"><div style="font-size:12px; color:#5C5C60;">Total Platform Budget</div><div style="font-size:28px; font-weight:700; color:var(--primary);">₹{int(total_est_cost):,}</div></div>')
        
    tab1, tab2, tab3 = st.tabs(["👥 User Directory", "✈️ Global Trips", "📝 Audit Logs"])
    
    # ---------------- TAB 1: USER MANAGEMENT ----------------
    with tab1:
        st.subheader("Manage Users")
        users_list = fetch_all("SELECT id, username, email, is_admin, created_at FROM users")
        
        for u in users_list:
            admin_badge = "🛡️ Admin" if u["is_admin"] else "👤 User"
            with st.container():
                html_markdown(
                    f"""
                    <div style="border: 1px solid var(--border); padding: 12px 18px; border-radius: 12px; margin-bottom: 10px; background: var(--card-bg);">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="font-weight:bold; font-size:15px;">{u['username']} <span style="font-size:11px; color:#A0AAB2; margin-left:10px;">({admin_badge})</span></span>
                            <span style="font-size:13px; color:#5C5C60;">{u['email']}</span>
                        </div>
                        <div style="font-size:11px; color:#A0AAB2; margin-top:5px;">Joined: {u['created_at']}</div>
                    </div>
                    """
                )
                
                # Check for delete button logic (cannot delete self)
                col1, col2 = st.columns([5, 1])
                with col2:
                    if u["id"] == user["id"]:
                        st.write("*(Current User)*")
                    else:
                        if st.button("Delete User", key=f"del_user_{u['id']}", type="secondary"):
                            # Delete user
                            try:
                                execute("DELETE FROM users WHERE id = ?", (u["id"],))
                                log_audit(user["id"], "user_deletion", f"Deleted user '{u['username']}' (ID: {u['id']}).")
                                st.toast(f"User {u['username']} deleted.")
                                st.rerun()
                            except Exception as exc:
                                logger.error(f"Failed to delete user ID {u['id']}: {exc}")
                                st.error("Failed to delete user.")
            st.markdown("<br>", unsafe_allow_html=True)
            
    # ---------------- TAB 2: GLOBAL TRIPS ----------------
    with tab2:
        st.subheader("Manage Planned Trips")
        all_trips = get_all_trips()
        
        if not all_trips:
            st.info("No trips have been planned on the platform yet.")
        else:
            for t in all_trips:
                with st.container():
                    html_markdown(
                        f"""
                        <div style="border: 1px solid var(--border); padding: 12px 18px; border-radius: 12px; margin-bottom: 10px; background: var(--card-bg);">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-weight:bold; font-size:15px;">📍 {t['destination']} <span style="font-size:11px; color:#A0AAB2; margin-left:10px;">(by {t['username']})</span></span>
                                <span style="font-size:13px; font-weight:600; color:var(--primary);">₹{int(t['estimated_cost']):,}</span>
                            </div>
                            <div style="font-size:13px; color:#5C5C60; margin-top:5px;">
                                {t['days']} days | {t['travelers']} travelers | {t['travel_type']} | {t['transport_mode']}
                            </div>
                            <div style="font-size:11px; color:#A0AAB2; margin-top:5px;">Created: {t['created_at']}</div>
                        </div>
                        """
                    )
                    col1, col2 = st.columns([5, 1])
                    with col2:
                        if st.button("Delete Trip", key=f"admin_del_trip_{t['id']}", type="secondary"):
                            if delete_trip(t["id"], user["id"], is_admin=True):
                                st.toast("Trip deleted successfully.")
                                st.rerun()
                            else:
                                st.error("Failed to delete trip.")
                st.markdown("<br>", unsafe_allow_html=True)

    # ---------------- TAB 3: SYSTEM AUDIT LOGS ----------------
    with tab3:
        st.subheader("Audit Event Logs")
        logs = fetch_all(
            """
            SELECT l.id, u.username, l.event_type, l.description, l.created_at 
            FROM audit_logs l 
            LEFT JOIN users u ON l.user_id = u.id 
            ORDER BY l.created_at DESC 
            LIMIT 100
            """
        )
        
        if not logs:
            st.info("No audit logs found.")
        else:
            log_df = pd.DataFrame(logs)
            log_df = log_df.rename(columns={
                "username": "User",
                "event_type": "Event",
                "description": "Description",
                "created_at": "Timestamp"
            })
            if "id" in log_df.columns:
                log_df = log_df.drop(columns=["id"])
                
            st.dataframe(
                log_df,
                use_container_width=True,
                column_config={
                    "Timestamp": st.column_config.TextColumn("Timestamp"),
                    "User": st.column_config.TextColumn("User"),
                    "Event": st.column_config.TextColumn("Event"),
                    "Description": st.column_config.TextColumn("Description")
                }
            )

def fetch_one_val(query: str, params: tuple = ()) -> Any:
    """Helper to fetch a single value from query."""
    res = fetch_all(query, params)
    if res:
        return list(res[0].values())[0]
    return None
