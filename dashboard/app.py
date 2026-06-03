import time
import requests
import streamlit as st
import pandas as pd

# Page setup
st.set_page_config(
    page_title="DevOps Monitoring Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style injection for a premium look
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    h1 {
        color: #1e3d59;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e1e8ed;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_URL = "http://localhost:8000"

st.title("📊 DevOps Monitoring Dashboard")

# Sidebar - API Configuration
st.sidebar.header("🔑 Authentication")
api_key = st.sidebar.text_input("X-API-Key", value="demo-key", type="password")

# Tabs
tab1, tab2 = st.tabs(["📈 System Metrics", "🖥️ Monitored Servers"])

# Tab 1: Metrics
with tab1:
    st.subheader("Real-Time Host Metrics")
    
    # Cache metrics for 2 seconds
    @st.cache_data(ttl=2)
    def fetch_metrics():
        try:
            resp = requests.get(f"{API_URL}/metrics", timeout=1.5)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    metrics_data = fetch_metrics()
    
    if metrics_data:
        # 3 Columns for metrics tiles
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("CPU Utilization", f"{metrics_data['cpu_percent']}%")
        with col2:
            st.metric("Memory Utilization", f"{metrics_data['memory_percent']}%", f"{metrics_data['memory_used_gb']} GB used")
        with col3:
            st.metric("Disk Utilization", f"{metrics_data['disk_percent']}%")
        
        # Accumulate metrics history in session state
        if "history" not in st.session_state:
            st.session_state.history = []
        
        # Avoid duplicate data points if timestamp or interval is too fast
        current_time = time.time()
        st.session_state.history.append({
            "Time": pd.to_datetime(current_time, unit='s'),
            "CPU %": metrics_data['cpu_percent'],
            "Memory %": metrics_data['memory_percent']
        })
        
        # Keep only the last 60 points
        if len(st.session_state.history) > 60:
            st.session_state.history = st.session_state.history[-60:]
            
        # Draw chart
        chart_df = pd.DataFrame(st.session_state.history)
        chart_df = chart_df.set_index("Time")
        st.line_chart(chart_df)
    else:
        st.error("Failed to connect to the FastAPI backend. Make sure it is running on port 8000.")

# Tab 2: Servers
with tab2:
    st.subheader("Manage Monitored Servers")

    # Cache server list for 5 seconds
    @st.cache_data(ttl=5)
    def fetch_servers():
        try:
            resp = requests.get(f"{API_URL}/servers", timeout=2.0)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return []

    servers = fetch_servers()
    
    if servers:
        # Convert to DataFrame
        df = pd.DataFrame(servers)
        # Select and reorder columns
        df = df[["id", "name", "host", "port", "status"]]
        
        # Coloring function
        def style_status(val):
            if val == "UP":
                return "background-color: #d4edda; color: #155724; font-weight: bold;"
            elif val == "DEGRADED":
                return "background-color: #fff3cd; color: #856404; font-weight: bold;"
            elif val == "DOWN":
                return "background-color: #f8d7da; color: #721c24; font-weight: bold;"
            return ""
            
        styled_df = df.style.map(style_status, subset=["status"])
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("No servers registered yet.")

    # Two columns: Add Server and Action Trigger
    col_add, col_action = st.columns(2)
    
    with col_add:
        st.markdown("### ➕ Register New Server")
        with st.form("add_server_form", clear_on_submit=True):
            name = st.text_input("Server Name", placeholder="api-prod-1")
            host = st.text_input("Host Address", placeholder="httpbin.org")
            port = st.number_input("Port", min_value=1, max_value=65535, value=80)
            submitted = st.form_submit_form_button = st.form_submit_button("Register")
            
            if submitted:
                if name and host:
                    headers = {"X-API-Key": api_key}
                    payload = {"name": name, "host": host, "port": port}
                    try:
                        resp = requests.post(f"{API_URL}/servers", json=payload, headers=headers)
                        if resp.status_code == 201:
                            st.success(f"Server '{name}' registered successfully!")
                            st.cache_data.clear()
                            st.rerun()
                        elif resp.status_code == 403:
                            st.error("Authentication failed: Invalid X-API-Key.")
                        else:
                            st.error(f"Failed to register server: {resp.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Please fill in both Name and Host.")

    with col_action:
        st.markdown("### ⚡ Health Check Trigger")
        if servers:
            server_options = {f"{s['id']} - {s['name']} ({s['host']})": s['id'] for s in servers}
            selected_label = st.selectbox("Select Server", list(server_options.keys()))
            selected_id = server_options[selected_label]
            
            if st.button("Trigger Immediate Check"):
                try:
                    resp = requests.post(f"{API_URL}/servers/{selected_id}/check")
                    if resp.status_code == 200:
                        updated_server = resp.json()
                        st.info(f"Check completed: Server is {updated_server['status']}")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"Failed to trigger health check: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
            
            st.markdown("### ❌ Remove Server")
            if st.button("Delete Selected Server"):
                try:
                    headers = {"X-API-Key": api_key}
                    resp = requests.delete(f"{API_URL}/servers/{selected_id}", headers=headers)
                    if resp.status_code == 204:
                        st.success("Server removed successfully!")
                        st.cache_data.clear()
                        st.rerun()
                    elif resp.status_code == 403:
                        st.error("Authentication failed: Invalid X-API-Key.")
                    else:
                        st.error(f"Failed to delete server: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.write("Register a server first to see actions.")

# Loop rerun for metrics tab
time.sleep(2)
st.rerun()
