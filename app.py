#!/usr/bin/env python3
"""
Lasers-PINN Designer Standalone Application.
An interactive Streamlit-based web dashboard that loads the trained PyTorch PINN model,
enables real-time parametric sweeps, and visualizes spatial hole burning and metrics.
"""

from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

# Setup paths
RUN_DIR = Path(__file__).resolve().parent
REPO_DIR = RUN_DIR.parents[1]
TOOLS_DIR = REPO_DIR / "Tools"


from pinn_surrogate import PINNSurrogate

def main():
    st.set_page_config(
        page_title="PLaser Designer",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for dark-mode premium look
    st.markdown("""
        <style>
        .main {
            background-color: #0d1117;
            color: #c9d1d9;
        }
        .sidebar .sidebar-content {
            background-color: #161b22;
        }
        h1, h2, h3, h4 {
            color: #58a6ff !important;
            font-family: 'Outfit', sans-serif;
        }
        .metric-card {
            background-color: #1f242c;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .metric-val {
            font-size: 2rem;
            font-weight: bold;
            color: #58a6ff;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #8b949e;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("⚡ PLaser Designer")
    st.write("Real-Time Parametric Telecom Diode Laser Design Simulator (PLaser) powered by Physics-Informed Neural Networks (PINN).")
    
    # Load the model
    @st.cache_resource
    def load_surrogate():
        return PINNSurrogate(RUN_DIR)
        
    try:
        surrogate = load_surrogate()
    except Exception as e:
        st.error(f"Error loading PINN model weights: {e}")
        st.info("Please run the training script first: `python train_pinn.py` to generate the model weights.")
        return
        
    # Sidebar design parameters
    st.sidebar.header("🔧 Design Parameters")
    
    st.sidebar.subheader("Facet Reflectivities")
    R1 = st.sidebar.slider("Left Mirror (HR) Reflectivity R1", 0.1, 0.95, 0.90, step=0.01)
    R2 = st.sidebar.slider("Right Mirror (AR) Reflectivity R2", 0.05, 0.50, 0.05, step=0.01)
    
    st.sidebar.subheader("Cavity Dimensions")
    L_um = st.sidebar.slider("Cavity Length L (μm)", 100, 1000, 300, step=50)
    
    st.sidebar.header("🔥 Operating Conditions")
    T0 = st.sidebar.slider("Ambient Temperature T0 (K)", 250, 360, 300, step=5)
    I_active = st.sidebar.slider("Active Region Injection Current (A)", 0.01, 0.50, 0.13, step=0.01)
    
    # Predict in real-time
    res = surrogate.predict(R1=R1, R2=R2, L_um=L_um, T0=T0, I_active=I_active)
    
    P_opt = res["P_opt"]
    wpe = res["wpe"]
    I_total = res["I_total"]
    N_prof = res["N"]
    P_prof = res["P"]
    z_grid = res["z_grid"]
    
    # Row 1: Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{P_opt*1000:.2f} mW</div>
                <div class="metric-label">Optical Output Power</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{wpe * 100:.3f} %</div>
                <div class="metric-label">Wall-Plug Efficiency (WPE)</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val">{I_total:.3f} A</div>
                <div class="metric-label">Total Terminal Current</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        # Physical analysis status
        status = "Inactive"
        color = "#ff3366"
        if P_opt > 0.0001:
            if wpe > 0.01:
                status = "Optimized Lasing"
                color = "#00ffcc"
            elif T0 > 325:
                status = "Thermal Droop"
                color = "#ffaa00"
            else:
                status = "Near Threshold"
                color = "#58a6ff"
        else:
            status = "Below Threshold"
            color = "#8b949e"
            
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-val" style="color: {color};">{status}</div>
                <div class="metric-label">Lasing State</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    
    # Row 2: Visualization Charts
    col_plot1, col_plot2 = st.columns(2)
    
    # Plot 1: Internal Optical Power
    with col_plot1:
        st.subheader("📈 Longitudinal Optical Power Profile")
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        ax1.plot(z_grid, P_prof, color="#ff3366", linewidth=2.5, label="Optical Power P(z)")
        ax1.set_xlabel("Cavity Position z (μm)", color="white")
        ax1.set_ylabel("Internal Power (W)", color="white")
        ax1.grid(True, linestyle="--", alpha=0.3, color="#555555")
        ax1.set_facecolor("#1e1e1e")
        fig1.patch.set_facecolor("#0d1117")
        ax1.tick_params(colors="white")
        for spine in ax1.spines.values():
            spine.set_color("#555555")
        ax1.legend(facecolor="#121212", edgecolor="#555555", labelcolor="white")
        st.pyplot(fig1)
        
    # Plot 2: Carrier Density (Spatial Hole Burning)
    with col_plot2:
        st.subheader("📉 Spatial Hole Burning (Carrier Density)")
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.plot(z_grid, N_prof / 1e18, color="#00ffcc", linewidth=2.5, label="Carrier Density N(z)")
        ax2.set_xlabel("Cavity Position z (μm)", color="white")
        ax2.set_ylabel("Carrier Density ($10^{18}$ cm$^{-3}$)", color="white")
        ax2.grid(True, linestyle="--", alpha=0.3, color="#555555")
        ax2.set_facecolor("#1e1e1e")
        fig2.patch.set_facecolor("#0d1117")
        ax2.tick_params(colors="white")
        for spine in ax2.spines.values():
            spine.set_color("#555555")
        ax2.legend(facecolor="#121212", edgecolor="#555555", labelcolor="white")
        st.pyplot(fig2)
        
    # Row 3: Design Guidance / Physical Insight
    st.subheader("💡 Physical Insights & Design Guidance")
    
    # Dynamic text based on current settings
    guidance = []
    
    if abs(R1 - R2) > 0.4:
        guidance.append("👉 **Facet Asymmetry:** The large difference between R1 (HR) and R2 (AR) skews the optical field distribution strongly towards the front facet (z = L). This is standard for edge-emitting diodes to maximize single-facet output power, but it causes significant **Spatial Hole Burning (SHB)**, which locally depletes carriers near the output facet.")
    else:
        guidance.append("👉 **Symmetric Cavity:** The symmetric mirror reflectivities yield a balanced, symmetric internal optical power and carrier density profile. While this is structurally simple, it results in equal power emission from both facets, which decreases the usable single-facet WPE unless external combining is used.")
        
    if T0 > 320:
        guidance.append("👉 **Thermal Degradation:** High ambient temperature ($T_0 > 320\text{ K}$) degrades performance. The logarithmic gain coefficient $g_0$ is reduced, and the transparency carrier density $N_{\text{tr}}$ is increased, requiring higher injection current to maintain threshold. Auger recombination losses also scale as $T_0^2$, causing thermal droop.")
        
    if P_opt < 0.001:
        guidance.append("👉 **Lasing Threshold:** The current injected is insufficient to overcome the cavity mirror losses ($\alpha_m = \\frac{1}{2L}\\ln(\\frac{1}{R_1 R_2})$) and internal loss ($\alpha_i = 10\text{ cm}^{-1}$). Increase the injection current or mirror reflectivities to achieve lasing.")
        
    for item in guidance:
        st.write(item)

if __name__ == "__main__":
    main()
