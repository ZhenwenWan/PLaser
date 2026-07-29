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
    
    st.markdown("<h3 style='margin: 0; padding-top: 10px; color: #58a6ff; font-family: \"Outfit\", sans-serif;'>⚡ PLaser Designer</h3>", unsafe_allow_html=True)
    
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
    
    # State logic based on model predictions
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

    # Display Metrics in the Sidebar left panel
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Lasing State:** <span style='color: {color}; font-weight: bold; font-size: 1.1rem;'>{status}</span>", unsafe_allow_html=True)
    st.sidebar.metric("Output Power (mW)", f"{P_opt * 1000.0:.2f}")
    st.sidebar.metric("Wall-Plug Efficiency (WPE)", f"{wpe * 100.0:.3f} %")
    st.sidebar.metric("Total Current (A)", f"{I_total:.3f}")
    
    st.write("")
    
    # 3 columns for 6 reduced viewports of distributions
    col_long, col_trans2d, col_trans1d = st.columns(3)
    
    # Column 1: Longitudinal Profiles (1D along cavity length)
    with col_long:
        # Plot 1: Carrier Density N(z)
        fig_n, ax_n = plt.subplots(figsize=(4.5, 3.2))
        ax_n.plot(z_grid, N_prof / 1e18, color="#ff7b72", linewidth=2.0, label="N(z)")
        ax_n.set_title("Carrier Density N(z)", color="white", fontsize=9, fontweight="bold")
        ax_n.set_xlabel("z Position (μm)", color="#8b949e", fontsize=7.5)
        ax_n.set_ylabel("N (10^18 cm^-3)", color="#8b949e", fontsize=7.5)
        ax_n.grid(True, linestyle="--", alpha=0.3, color="#555555")
        ax_n.set_facecolor("#1e1e1e")
        fig_n.patch.set_facecolor("#0d1117")
        ax_n.tick_params(colors="#8b949e", labelsize=7.5)
        ax_n.set_box_aspect(0.65)
        for spine in ax_n.spines.values():
            spine.set_color("#30363d")
        fig_n.tight_layout()
        st.pyplot(fig_n)
        
        # Plot 2: Optical Power P(z)
        fig_p, ax_p = plt.subplots(figsize=(4.5, 3.2))
        ax_p.plot(z_grid, P_prof * 1000.0, color="#64ffda", linewidth=2.0, label="P(z)")
        ax_p.set_title("Optical Power Profile P(z)", color="white", fontsize=9, fontweight="bold")
        ax_p.set_xlabel("z Position (μm)", color="#8b949e", fontsize=7.5)
        ax_p.set_ylabel("Power (mW)", color="#8b949e", fontsize=7.5)
        ax_p.grid(True, linestyle="--", alpha=0.3, color="#555555")
        ax_p.set_facecolor("#1e1e1e")
        fig_p.patch.set_facecolor("#0d1117")
        ax_p.tick_params(colors="#8b949e", labelsize=7.5)
        ax_p.set_box_aspect(0.65)
        for spine in ax_p.spines.values():
            spine.set_color("#30363d")
        fig_p.tight_layout()
        st.pyplot(fig_p)
        
        st.subheader("1D Longitudinal")

    # Column 2: 2D Transverse Distributions
    with col_trans2d:
        # 2D transverse grid
        tx = np.linspace(-3.5, 3.5, 40)
        ty = np.linspace(-2.0, 2.0, 40)
        TX, TY = np.meshgrid(tx, ty)
        
        # Plot 3: 2D Mode intensity
        fig_m2d, ax_m2d = plt.subplots(figsize=(4.5, 3.2))
        norm_power = max(0.001, P_opt * 1000.0 / 250.0)
        I_mode = norm_power * np.exp(-TX**2 / 1.5**2 - TY**2 / 0.5**2)
        contour_m = ax_m2d.contourf(TX, TY, I_mode, levels=15, cmap="inferno")
        ax_m2d.set_title("Mode Intensity Shape |Ψ|²", color="white", fontsize=9, fontweight="bold")
        ax_m2d.set_xlabel("x width (μm)", color="#8b949e", fontsize=7.5)
        ax_m2d.set_ylabel("y height (μm)", color="#8b949e", fontsize=7.5)
        ax_m2d.tick_params(colors="#8b949e", labelsize=7.5)
        ax_m2d.set_box_aspect(0.65)
        for spine in ax_m2d.spines.values():
            spine.set_color("#30363d")
        # Add active region waveguide bounds
        rect = plt.Rectangle((-1.4, -0.171), 2.8, 0.342, fill=False, edgecolor="#ffffff", linestyle=":", alpha=0.5)
        ax_m2d.add_patch(rect)
        fig_m2d.tight_layout()
        st.pyplot(fig_m2d)
        
        # Plot 4: 2D Temperature heat map
        fig_t2d, ax_t2d = plt.subplots(figsize=(4.5, 3.2))
        heating_power = max(0.0, I_total * 1.05 - P_opt)
        delta_T = 18.0 * heating_power * (T0 / 300.0)**1.5
        T_trans = T0 + delta_T * np.exp(-TX**2 / 2.0**2) * ((TY + 2.0)/2.0) * np.exp(-TY**2 / 0.8**2)
        contour_t = ax_t2d.contourf(TX, TY, T_trans, levels=15, cmap="hot")
        ax_t2d.set_title("Temperature Heat Map T(x,y)", color="white", fontsize=9, fontweight="bold")
        ax_t2d.set_xlabel("x width (μm)", color="#8b949e", fontsize=7.5)
        ax_t2d.set_ylabel("y height (μm)", color="#8b949e", fontsize=7.5)
        ax_t2d.tick_params(colors="#8b949e", labelsize=7.5)
        ax_t2d.set_box_aspect(0.65)
        for spine in ax_t2d.spines.values():
            spine.set_color("#30363d")
        fig_t2d.tight_layout()
        st.pyplot(fig_t2d)
        
        st.subheader("2D Transverse")

    # Column 3: 1D Transverse Slices
    with col_trans1d:
        # Plot 5: Horizontal slice
        fig_sh, ax_sh = plt.subplots(figsize=(4.5, 3.2))
        I_horiz = norm_power * np.exp(-tx**2 / 1.5**2)
        ax_sh.plot(tx, I_horiz, color="#ffcc00", linewidth=2.0, label="Horizontal Mode slice")
        ax_sh.set_title("Horizontal Cut Mode Profile", color="white", fontsize=9, fontweight="bold")
        ax_sh.set_xlabel("x width (μm)", color="#8b949e", fontsize=7.5)
        ax_sh.set_ylabel("Intensity", color="#8b949e", fontsize=7.5)
        ax_sh.grid(True, linestyle="--", alpha=0.3, color="#555555")
        ax_sh.set_facecolor("#1e1e1e")
        fig_sh.patch.set_facecolor("#0d1117")
        ax_sh.tick_params(colors="#8b949e", labelsize=7.5)
        ax_sh.set_box_aspect(0.65)
        for spine in ax_sh.spines.values():
            spine.set_color("#30363d")
        fig_sh.tight_layout()
        st.pyplot(fig_sh)
        
        # Plot 6: Vertical slice
        fig_sv, ax_sv = plt.subplots(figsize=(4.5, 3.2))
        I_vert = norm_power * np.exp(-ty**2 / 0.5**2)
        ax_sv.plot(ty, I_vert, color="#ff33cc", linewidth=2.0, label="Vertical Mode slice")
        ax_sv.set_title("Vertical Cut Mode Profile", color="white", fontsize=9, fontweight="bold")
        ax_sv.set_xlabel("y height (μm)", color="#8b949e", fontsize=7.5)
        ax_sv.set_ylabel("Intensity", color="#8b949e", fontsize=7.5)
        ax_sv.grid(True, linestyle="--", alpha=0.3, color="#555555")
        ax_sv.set_facecolor("#1e1e1e")
        fig_sv.patch.set_facecolor("#0d1117")
        ax_sv.tick_params(colors="#8b949e", labelsize=7.5)
        ax_sv.set_box_aspect(0.65)
        for spine in ax_sv.spines.values():
            spine.set_color("#30363d")
        fig_sv.tight_layout()
        st.pyplot(fig_sv)
        
        st.subheader("1D Transverse")
        
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
