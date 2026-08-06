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
from matplotlib.colors import LinearSegmentedColormap
import streamlit as st

# Setup paths
RUN_DIR = Path(__file__).resolve().parent
REPO_DIR = RUN_DIR.parents[1]
TOOLS_DIR = REPO_DIR / "Tools"


from pinn_surrogate import PINNSurrogate

def main():
    # Define uniform dark blue plot style colormaps
    cmap_mode = LinearSegmentedColormap.from_list("mode_cmap", ["#172a45", "#4e1b6f", "#9e2a2b", "#ff9f1c", "#ffffff"])
    cmap_temp = LinearSegmentedColormap.from_list("temp_cmap", ["#172a45", "#990000", "#ff5500", "#ffcc00", "#ffffff"])

    st.set_page_config(
        page_title="PLaser Designer",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for dark-mode premium look and layout compaction
    st.markdown("""
        <style>
        [data-testid="stHeader"] {
            display: none;
        }
        .block-container {
            padding-top: 0.2rem !important;
            padding-bottom: 0rem !important;
        }
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
            margin-top: 0px !important;
            margin-bottom: 5px !important;
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
    
    st.markdown("<h3 style='margin: 0px; padding-top: 0px; color: #58a6ff; font-family: \"Outfit\", sans-serif;'>⚡ PLaser Designer</h3>", unsafe_allow_html=True)
    
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
    # Initialize session state for design parameters if not present
    if "R1" not in st.session_state:
        st.session_state.R1 = 0.90
    if "R2" not in st.session_state:
        st.session_state.R2 = 0.05
    if "L_um" not in st.session_state:
        st.session_state.L_um = 300
    if "T0" not in st.session_state:
        st.session_state.T0 = 300
    if "I_active" not in st.session_state:
        st.session_state.I_active = 0.13
    if "enable_geom" not in st.session_state:
        st.session_state.enable_geom = False
    if "w_active" not in st.session_state:
        st.session_state.w_active = 2.8
    if "d_active" not in st.session_state:
        st.session_state.d_active = 0.342
        
    # View Mode Selector at the top of the sidebar
    mode = st.sidebar.radio("View Mode", ["📊 Multi-Physics Dashboard", "👁️ 3D Cavity Field Analyzer"])

    if mode == "📊 Multi-Physics Dashboard":
        st.sidebar.header("🔧 Design Parameters")
        st.sidebar.subheader("Facet Reflectivities")
        R1 = st.sidebar.slider("Left Mirror (HR) Reflectivity R1", 0.1, 0.95, st.session_state.R1, step=0.01)
        R2 = st.sidebar.slider("Right Mirror (AR) Reflectivity R2", 0.05, 0.50, st.session_state.R2, step=0.01)
        
        st.sidebar.subheader("Cavity Dimensions")
        L_um = st.sidebar.slider("Cavity Length L (μm)", 100, 1000, st.session_state.L_um, step=50)
        
        enable_geom = st.sidebar.checkbox("📐 Enable Custom Geometry", value=st.session_state.enable_geom)
        if enable_geom:
            w_active = st.sidebar.slider("Active Region Width w (μm)", 1.5, 4.0, st.session_state.w_active, step=0.1)
            d_active = st.sidebar.slider("Active Region Thickness d (μm)", 0.10, 0.50, st.session_state.d_active, step=0.01)
        else:
            w_active = 2.8
            d_active = 0.342
            
        st.sidebar.header("🔥 Operating Conditions")
        T0 = st.sidebar.slider("Ambient Temperature T0 (K)", 250, 360, st.session_state.T0, step=5)
        I_active = st.sidebar.slider("Active Region Injection Current (A)", 0.01, 0.50, st.session_state.I_active, step=0.01)
        
        # Save current values to session state
        st.session_state.R1 = R1
        st.session_state.R2 = R2
        st.session_state.L_um = L_um
        st.session_state.enable_geom = enable_geom
        st.session_state.w_active = w_active
        st.session_state.d_active = d_active
        st.session_state.T0 = T0
        st.session_state.I_active = I_active
    else:
        # Retain last values when in 3D Analyzer mode
        R1 = st.session_state.R1
        R2 = st.session_state.R2
        L_um = st.session_state.L_um
        enable_geom = st.session_state.enable_geom
        w_active = st.session_state.w_active
        d_active = st.session_state.d_active
        T0 = st.session_state.T0
        I_active = st.session_state.I_active

    # Predict in real-time
    res = surrogate.predict(
        R1=R1,
        R2=R2,
        L_um=L_um,
        T0=T0,
        I_active=I_active,
        w_active_um=w_active,
        d_active_um=d_active
    )
    
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
        c    # Display metrics or slice selector in the sidebar
    if mode == "📊 Multi-Physics Dashboard":
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Lasing State:** <span style='color: {color}; font-weight: bold; font-size: 1.1rem;'>{status}</span>", unsafe_allow_html=True)
        st.sidebar.metric("Output Power (mW)", f"{P_opt * 1000.0:.2f}")
        st.sidebar.metric("Wall-Plug Efficiency (WPE)", f"{wpe * 100.0:.3f} %")
        st.sidebar.metric("Total Current (A)", f"{I_total:.3f}")
    else:
        st.sidebar.header("👁️ 3D Cavity Controller")
        z_sel = st.sidebar.slider("Inspect Cavity Position z (μm)", min_value=0.0, max_value=float(L_um), value=float(L_um), step=float(L_um)/50.0)
        idx = int(np.clip(round(z_sel / (float(L_um) / 50.0)), 0, 50))
        
        st.sidebar.markdown("""
        <div style="background-color: #1f242c; border: 1px solid #30363d; border-radius: 6px; padding: 10px; margin-top: 10px;">
            <p style="margin: 0; color: #8b949e; font-size: 0.85rem;">Local z Position: <strong style="color: #58a6ff;">{:.1f} μm</strong></p>
            <p style="margin: 4px 0 0 0; color: #8b949e; font-size: 0.85rem;">Local Carrier Density N(z): <strong style="color: #ff7b72;">{:.3f} × 10¹⁸</strong></p>
            <p style="margin: 4px 0 0 0; color: #8b949e; font-size: 0.85rem;">Local Optical Power P(z): <strong style="color: #64ffda;">{:.1f} mW</strong></p>
        </div>
        """.format(z_grid[idx], N_prof[idx] / 1e18, P_prof[idx] * 1000.0), unsafe_allow_html=True)

    # Main area content rendering based on mode
    if mode == "📊 Multi-Physics Dashboard":
        # 3 columns for 6 reduced viewports of distributions
        col_long, col_trans2d, col_trans1d = st.columns(3)
        
        # Column 1: Longitudinal Profiles (1D along cavity length)
        with col_long:
            # Plot 1: Carrier Density N(z)
            fig_n = plt.figure(figsize=(4.5, 2.3))
            ax_n = fig_n.add_axes([0.18, 0.20, 0.72, 0.68])
            ax_n.plot(z_grid, N_prof / 1e18, color="#ff7b72", linewidth=2.0, label="N(z)")
            ax_n.set_title("Carrier Density N(z)", color="white", fontsize=9, fontweight="bold")
            ax_n.set_xlabel("z Position (μm)", color="#8b949e", fontsize=7.5)
            ax_n.set_ylabel("N (10^18 cm^-3)", color="#8b949e", fontsize=7.5)
            ax_n.grid(True, linestyle="--", alpha=0.3, color="#233554")
            ax_n.set_facecolor("#172a45")
            fig_n.patch.set_facecolor("#0d1117")
            ax_n.tick_params(colors="#8b949e", labelsize=7.5)
            for spine in ax_n.spines.values():
                spine.set_color("#30363d")
            st.pyplot(fig_n, use_container_width=True)
            
            # Plot 2: Optical Power P(z)
            fig_p = plt.figure(figsize=(4.5, 2.3))
            ax_p = fig_p.add_axes([0.18, 0.20, 0.72, 0.68])
            ax_p.plot(z_grid, P_prof * 1000.0, color="#64ffda", linewidth=2.0, label="P(z)")
            ax_p.set_title("Optical Power Profile P(z)", color="white", fontsize=9, fontweight="bold")
            ax_p.set_xlabel("z Position (μm)", color="#8b949e", fontsize=7.5)
            ax_p.set_ylabel("Power (mW)", color="#8b949e", fontsize=7.5)
            ax_p.grid(True, linestyle="--", alpha=0.3, color="#233554")
            ax_p.set_facecolor("#172a45")
            fig_p.patch.set_facecolor("#0d1117")
            ax_p.tick_params(colors="#8b949e", labelsize=7.5)
            for spine in ax_p.spines.values():
                spine.set_color("#30363d")
            st.pyplot(fig_p, use_container_width=True)

        # Column 2: 2D Transverse Distributions
        with col_trans2d:
            # 2D transverse grid
            tx = np.linspace(-3.5, 3.5, 40)
            ty = np.linspace(-2.0, 2.0, 40)
            TX, TY = np.meshgrid(tx, ty)
            
            w_waist = 1.5 * (w_active / 2.8)
            d_waist = 0.5 * (d_active / 0.342)
            w_thermal = 2.0 * (w_active / 2.8)
            
            # Plot 3: 2D Mode intensity
            fig_m2d = plt.figure(figsize=(4.5, 2.3))
            ax_m2d = fig_m2d.add_axes([0.18, 0.20, 0.72, 0.68])
            norm_power = max(0.001, P_opt * 1000.0 / 250.0)
            I_mode = 0.3 * norm_power * np.exp(-TX**2 / w_waist**2 - TY**2 / d_waist**2)
            contour_m = ax_m2d.contourf(TX, TY, I_mode, levels=15, cmap=cmap_mode, vmin=0, vmax=0.36)
            ax_m2d.set_title("Mode Intensity Shape |Ψ|²", color="white", fontsize=9, fontweight="bold")
            ax_m2d.set_xlabel("x width (μm)", color="#8b949e", fontsize=7.5)
            ax_m2d.set_ylabel("y height (μm)", color="#8b949e", fontsize=7.5)
            ax_m2d.tick_params(colors="#8b949e", labelsize=7.5)
            ax_m2d.set_facecolor("#172a45")
            fig_m2d.patch.set_facecolor("#0d1117")
            for spine in ax_m2d.spines.values():
                spine.set_color("#30363d")
            # Add active region waveguide bounds
            rect = plt.Rectangle((-w_active/2.0, -d_active/2.0), w_active, d_active, fill=False, edgecolor="#ffffff", linestyle=":", alpha=0.5)
            ax_m2d.add_patch(rect)
            ax_m2d.text(0, -d_active/2.0 - 0.3, f"Active Region ({w_active:.1f} x {d_active:.3f} μm)", color="white", fontsize=6.5, ha="center", alpha=0.7)
            st.pyplot(fig_m2d, use_container_width=True)
            
            # Plot 4: 2D Temperature heat map
            fig_t2d = plt.figure(figsize=(4.5, 2.3))
            ax_t2d = fig_t2d.add_axes([0.18, 0.20, 0.72, 0.68])
            heating_power = max(0.0, I_total * 1.05 - P_opt)
            delta_T = 18.0 * heating_power * (T0 / 300.0)**1.5
            T_trans = T0 + delta_T * np.exp(-TX**2 / w_thermal**2) * ((TY + 2.0)/2.0) * np.exp(-TY**2 / 0.8**2)
            contour_t = ax_t2d.contourf(TX, TY, T_trans, levels=15, cmap=cmap_temp, vmin=250.0, vmax=385.0)
            ax_t2d.set_title("Temperature Heat Map T(x,y)", color="white", fontsize=9, fontweight="bold")
            ax_t2d.set_xlabel("x width (μm)", color="#8b949e", fontsize=7.5)
            ax_t2d.set_ylabel("y height (μm)", color="#8b949e", fontsize=7.5)
            ax_t2d.tick_params(colors="#8b949e", labelsize=7.5)
            ax_t2d.set_facecolor("#172a45")
            fig_t2d.patch.set_facecolor("#0d1117")
            for spine in ax_t2d.spines.values():
                spine.set_color("#30363d")
            ax_t2d.axhline(y=-2.0, color="white", linestyle="-", linewidth=1.2, alpha=0.8)
            ax_t2d.text(0, -1.8, "Copper Heat Sink Mount (T0)", color="white", fontsize=6.5, ha="center", fontweight="bold")
            st.pyplot(fig_t2d, use_container_width=True)

        # Column 3: 1D Transverse Slices
        with col_trans1d:
            # Plot 5: Horizontal slice
            fig_sh = plt.figure(figsize=(4.5, 2.3))
            ax_sh = fig_sh.add_axes([0.18, 0.20, 0.72, 0.68])
            I_horiz = 0.3 * norm_power * np.exp(-tx**2 / w_waist**2)
            ax_sh.plot(tx, I_horiz, color="#ffcc00", linewidth=2.0, label="Horizontal Mode slice")
            ax_sh.set_title("Horizontal Cut Mode Profile", color="white", fontsize=9, fontweight="bold")
            ax_sh.set_xlabel("x width (μm)", color="#8b949e", fontsize=7.5)
            ax_sh.set_ylabel("Intensity", color="#8b949e", fontsize=7.5)
            ax_sh.grid(True, linestyle="--", alpha=0.3, color="#233554")
            ax_sh.set_facecolor("#172a45")
            fig_sh.patch.set_facecolor("#0d1117")
            ax_sh.tick_params(colors="#8b949e", labelsize=7.5)
            ax_sh.set_ylim(0.0, 0.36)
            for spine in ax_sh.spines.values():
                spine.set_color("#30363d")
            st.pyplot(fig_sh, use_container_width=True)
            
            # Plot 6: Vertical slice
            fig_sv = plt.figure(figsize=(4.5, 2.3))
            ax_sv = fig_sv.add_axes([0.18, 0.20, 0.72, 0.68])
            I_vert = 0.3 * norm_power * np.exp(-ty**2 / d_waist**2)
            ax_sv.plot(ty, I_vert, color="#ff33cc", linewidth=2.0, label="Vertical Mode slice")
            ax_sv.set_title("Vertical Cut Mode Profile", color="white", fontsize=9, fontweight="bold")
            ax_sv.set_xlabel("y height (μm)", color="#8b949e", fontsize=7.5)
            ax_sv.set_ylabel("Intensity", color="#8b949e", fontsize=7.5)
            ax_sv.grid(True, linestyle="--", alpha=0.3, color="#233554")
            ax_sv.set_facecolor("#172a45")
            fig_sv.patch.set_facecolor("#0d1117")
            ax_sv.tick_params(colors="#8b949e", labelsize=7.5)
            ax_sv.set_ylim(0.0, 0.36)
            for spine in ax_sv.spines.values():
                spine.set_color("#30363d")
            st.pyplot(fig_sv, use_container_width=True)
            
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

    else:
        # 2D transverse slices at selected z
        col_slice_mode, col_slice_temp = st.columns(2)
        
        tx = np.linspace(-3.5, 3.5, 40)
        ty = np.linspace(-2.0, 2.0, 40)
        TX, TY = np.meshgrid(tx, ty)

        with col_slice_mode:
            w_waist_z = 1.5 * (w_active / 2.8)
            d_waist_z = 0.5 * (d_active / 0.342)
            w_thermal = 2.0 * (w_active / 2.8)
            
            fig_m2d_z = plt.figure(figsize=(4.5, 2.3))
            ax_m2d_z = fig_m2d_z.add_axes([0.18, 0.20, 0.72, 0.68])
            norm_power_z = max(0.001, P_prof[idx] * 1000.0 / 250.0)
            I_mode_z = 0.3 * norm_power_z * np.exp(-TX**2 / w_waist_z**2 - TY**2 / d_waist_z**2)
            contour_m_z = ax_m2d_z.contourf(TX, TY, I_mode_z, levels=15, cmap=cmap_mode, vmin=0, vmax=0.36)
            ax_m2d_z.set_title(f"Local Optical Mode at z = {z_grid[idx]:.1f} μm", color="white", fontsize=9, fontweight="bold")
            ax_m2d_z.set_xlabel("x width (μm)", color="#8b949e", fontsize=7.5)
            ax_m2d_z.set_ylabel("y height (μm)", color="#8b949e", fontsize=7.5)
            ax_m2d_z.tick_params(colors="#8b949e", labelsize=7.5)
            ax_m2d_z.set_facecolor("#172a45")
            fig_m2d_z.patch.set_facecolor("#0d1117")
            for spine in ax_m2d_z.spines.values():
                spine.set_color("#30363d")
            rect = plt.Rectangle((-w_active/2.0, -d_active/2.0), w_active, d_active, fill=False, edgecolor="#ffffff", linestyle=":", alpha=0.5)
            ax_m2d_z.add_patch(rect)
            ax_m2d_z.text(0, -d_active/2.0 - 0.3, f"Active Region ({w_active:.1f} x {d_active:.3f} μm)", color="white", fontsize=6.5, ha="center", alpha=0.7)
            st.pyplot(fig_m2d_z, use_container_width=True)
            
        with col_slice_temp:
            fig_t2d_z = plt.figure(figsize=(4.5, 2.3))
            ax_t2d_z = fig_t2d_z.add_axes([0.18, 0.20, 0.72, 0.68])
            # Scale temperature rise based on local power ratio
            P_avg = max(1e-5, np.mean(P_prof))
            T_scale_z = P_prof[idx] / P_avg
            heating_power = max(0.0, I_total * 1.05 - P_opt)
            delta_T = 18.0 * heating_power * (T0 / 300.0)**1.5
            T_trans_z = T0 + delta_T * T_scale_z * np.exp(-TX**2 / w_thermal**2) * ((TY + 2.0)/2.0) * np.exp(-TY**2 / 0.8**2)
            
            contour_t_z = ax_t2d_z.contourf(TX, TY, T_trans_z, levels=15, cmap=cmap_temp, vmin=250.0, vmax=385.0)
            ax_t2d_z.set_title(f"Local Temperature at z = {z_grid[idx]:.1f} μm", color="white", fontsize=9, fontweight="bold")
            ax_t2d_z.set_xlabel("x width (μm)", color="#8b949e", fontsize=7.5)
            ax_t2d_z.set_ylabel("y height (μm)", color="#8b949e", fontsize=7.5)
            ax_t2d_z.tick_params(colors="#8b949e", labelsize=7.5)
            ax_t2d_z.set_facecolor("#172a45")
            fig_t2d_z.patch.set_facecolor("#0d1117")
            for spine in ax_t2d_z.spines.values():
                spine.set_color("#30363d")
            ax_t2d_z.axhline(y=-2.0, color="white", linestyle="-", linewidth=1.2, alpha=0.8)
            ax_t2d_z.text(0, -1.8, "Copper Heat Sink Mount (T0)", color="white", fontsize=6.5, ha="center", fontweight="bold")
            st.pyplot(fig_t2d_z, use_container_width=True)
            
        # 3D surface plots showing complete cavity profile
        col_3d_mode, col_3d_temp = st.columns(2)
        
        TX_3d, TZ_3d = np.meshgrid(tx, z_grid)
        
        with col_3d_mode:
            fig_3d_m = plt.figure(figsize=(5, 1.3))
            ax_3d_m = fig_3d_m.add_subplot(111, projection="3d")
            I_3d = 0.3 * (P_prof[:, None] * 1000.0 / 250.0) * np.exp(-TX_3d**2 / w_waist_z**2)
            surf_m = ax_3d_m.plot_surface(TX_3d, TZ_3d, I_3d, cmap=cmap_mode, edgecolor="none", antialiased=True, vmin=0, vmax=0.36)
            ax_3d_m.set_title("3D Optical Intensity |Ψ(x, 0, z)|²", color="white", fontsize=9.5, fontweight="bold")
            ax_3d_m.set_xlabel("x width (μm)", color="#8b949e", fontsize=7)
            ax_3d_m.set_ylabel("z Position (μm)", color="#8b949e", fontsize=7)
            ax_3d_m.set_zlabel("Intensity", color="#8b949e", fontsize=7)
            ax_3d_m.set_box_aspect((1.5, 1.0, 0.45))
            ax_3d_m.view_init(elev=20, azim=-55)
            fig_3d_m.subplots_adjust(left=-0.05, right=1.05, bottom=-0.05, top=1.05)
            ax_3d_m.xaxis.set_pane_color((0.09, 0.16, 0.27, 1.0))
            ax_3d_m.yaxis.set_pane_color((0.09, 0.16, 0.27, 1.0))
            ax_3d_m.zaxis.set_pane_color((0.09, 0.16, 0.27, 1.0))
            ax_3d_m.tick_params(colors="#8b949e", labelsize=6.5)
            ax_3d_m.xaxis.label.set_color("#8b949e")
            ax_3d_m.yaxis.label.set_color("#8b949e")
            ax_3d_m.zaxis.label.set_color("#8b949e")
            fig_3d_m.patch.set_facecolor("#0d1117")
            ax_3d_m.set_facecolor("#0d1117")
            st.pyplot(fig_3d_m, use_container_width=True)
            
        with col_3d_temp:
            fig_3d_t = plt.figure(figsize=(5, 1.3))
            ax_3d_t = fig_3d_t.add_subplot(111, projection="3d")
            T_3d = T0 + delta_T * (P_prof[:, None] / P_avg) * np.exp(-TX_3d**2 / w_thermal**2)
            surf_t = ax_3d_t.plot_surface(TX_3d, TZ_3d, T_3d, cmap=cmap_temp, edgecolor="none", antialiased=True, vmin=250.0, vmax=385.0)
            ax_3d_t.set_title("3D Temperature Profile T(x, 0, z)", color="white", fontsize=9.5, fontweight="bold")
            ax_3d_t.set_xlabel("x width (μm)", color="#8b949e", fontsize=7)
            ax_3d_t.set_ylabel("z Position (μm)", color="#8b949e", fontsize=7)
            ax_3d_t.set_zlabel("Temp (K)", color="#8b949e", fontsize=7)
            ax_3d_t.set_box_aspect((1.5, 1.0, 0.45))
            ax_3d_t.view_init(elev=20, azim=-55)
            fig_3d_t.subplots_adjust(left=-0.05, right=1.05, bottom=-0.05, top=1.05)
            ax_3d_t.xaxis.set_pane_color((0.09, 0.16, 0.27, 1.0))
            ax_3d_t.yaxis.set_pane_color((0.09, 0.16, 0.27, 1.0))
            ax_3d_t.zaxis.set_pane_color((0.09, 0.16, 0.27, 1.0))
            ax_3d_t.tick_params(colors="#8b949e", labelsize=6.5)
            ax_3d_t.xaxis.label.set_color("#8b949e")
            ax_3d_t.yaxis.label.set_color("#8b949e")
            ax_3d_t.zaxis.label.set_color("#8b949e")
            fig_3d_t.patch.set_facecolor("#0d1117")
            ax_3d_t.set_facecolor("#0d1117")
            st.pyplot(fig_3d_t, use_container_width=True)

if __name__ == "__main__":
    main()
