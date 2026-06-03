import streamlit as st
import pandas as pd
import xgboost as xgb
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Enterprise BMS Dashboard", layout="wide")

st.markdown("""
<style>
    .kpi-card { background: rgba(30, 33, 36, 0.6); border: 1px solid #444; border-radius: 12px; padding: 20px; backdrop-filter: blur(10px); }
    .stApp { background-color: #0e1117; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_assets():
    model = xgb.XGBRegressor()
    model.load_model("../models/xgboost_capacity_model.json")
    df_sample = pd.read_csv("../data/dashboard_sample.csv")
    return model, df_sample


try:
    model, sample_df = load_assets()
except Exception as e:
    st.error("Failed to load model or data. Please ensure the training script has completed successfully.")
    st.stop()

st.title("🔋 Battery Management System - Advanced Analytics")

packet_id = st.sidebar.selectbox("Telemetry Packet ID", sample_df.index)
current_data = sample_df.iloc[packet_id].copy()

features_cols = ['Cycle_in_Battery', 'Max_Temp', 'Avg_Temp', 'Avg_Discharge_Load', 'Cutoff_Voltage']
features = current_data[features_cols].values.reshape(1, -1)

# Predictions
pred_cap = float(model.predict(features)[0])
actual_cap = float(current_data['Actual_Capacity'])
soh = max(0, min(100, ((pred_cap - 1.4) / (2.0 - 1.4)) * 100))

col1, col2 = st.columns([1, 2])

with col1:
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=soh,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "State of Health (SOH) %", 'font': {'color': 'white'}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': "white"},
            'bar': {'color': "#00E676" if soh > 50 else "#FF3D00"},
            'bgcolor': "black",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [{'range': [0, 50], 'color': "#331111"}, {'range': [50, 100], 'color': "#113311"}]
        }
    ))
    fig_gauge.update_layout(height=300, template="plotly_dark", margin=dict(l=20, r=20, t=50, b=20),
                            paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_gauge, use_container_width=True)

with col2:
    start_cycle = int(current_data['Cycle_in_Battery'])
    end_cycle = 200

    if start_cycle < end_cycle:
        cycles = np.arange(start_cycle, end_cycle + 1)
        sim_data = pd.DataFrame({
            'Cycle_in_Battery': cycles,
            'Max_Temp': current_data['Max_Temp'],
            'Avg_Temp': current_data['Avg_Temp'],
            'Avg_Discharge_Load': current_data['Avg_Discharge_Load'],
            'Cutoff_Voltage': current_data['Cutoff_Voltage']
        })

        fig_line = go.Figure()

        # Area chart with glow
        fig_line.add_trace(go.Scatter(
            x=cycles, y=model.predict(sim_data[features_cols]),
            mode='lines', name='Degradation Path',
            line=dict(color='#00B0FF', width=4),
            fill='tozeroy', fillcolor='rgba(0, 176, 255, 0.1)'
        ))

        # Red failure threshold
        fig_line.add_trace(go.Scatter(
            x=[cycles[0], cycles[-1]], y=[1.4, 1.4],
            mode='lines', name='Failure Point',
            line=dict(color='#FF3D00', width=3, dash='dot')
        ))

        fig_line.update_layout(
            template="plotly_dark",
            title="Predictive Degradation Trajectory",
            xaxis_title="Future Cycles",
            yaxis_title="Capacity (Ah)",
            hovermode="x unified",
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("Telemetry packet cycle exceeds projection limit. End of life reached.")

st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Predicted Capacity", f"{pred_cap:.3f} Ah")
c2.metric("Actual Sensor Capacity", f"{actual_cap:.3f} Ah")
c3.metric("Calculation Error", f"{abs(pred_cap - actual_cap):.3f} Ah")
c4.metric("Discharge Load", f"{current_data['Avg_Discharge_Load']:.2f} A")

st.markdown("### Live Telemetry Stream")
st.dataframe(current_data[features_cols].to_frame().T, use_container_width=True)