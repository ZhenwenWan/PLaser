#!/usr/bin/env python3
"""
Generate a high-fidelity MP4 demonstration video for PLaser.
Sweeps design parameters in real-time and visualizes multiphysics steady states.
Simulates the entire Streamlit interface (sidebar controller + viewports).
Demos both View Modes: Multi-Physics Dashboard and 3D Cavity Field Analyzer.
"""

import sys
from pathlib import Path

# Dependency Check
try:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import LinearSegmentedColormap
    import cv2
except ImportError as e:
    print(f"Dependency Error: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)

# Conditional path injection for local PyTorch libs
try:
    import torch
except ImportError:
    libs_path = r"C:\Users\aw4wz\Documents\Codex\Lasers\Lasers\Libs"
    import os
    if os.path.exists(libs_path):
        sys.path.insert(0, libs_path)
    try:
        import torch
    except ImportError:
        print("Error: PyTorch not found. Please activate virtual environment or install torch.")
        sys.exit(1)

# Import PLaser surrogate wrapper
try:
    from pinn_surrogate import PINNSurrogate
except ImportError as e:
    print(f"Error importing pinn_surrogate: {e}")
    sys.exit(1)

# Setup paths
PLASER_DIR = Path(__file__).resolve().parent

# Preload Cisco OpenH264 DLL using ctypes
dll_path = PLASER_DIR / "openh264-1.8.0-win64.dll"
if dll_path.exists():
    try:
        import ctypes
        ctypes.CDLL(str(dll_path))
        print("Successfully preloaded Cisco OpenH264 DLL.")
    except Exception as e:
        print(f"Warning: Failed to preload OpenH264 DLL: {e}")

surrogate = PINNSurrogate(PLASER_DIR)

# Define uniform dark blue plot style colormaps
cmap_mode = LinearSegmentedColormap.from_list("mode_cmap", ["#172a45", "#4e1b6f", "#9e2a2b", "#ff9f1c", "#ffffff"])
cmap_temp = LinearSegmentedColormap.from_list("temp_cmap", ["#172a45", "#990000", "#ff5500", "#ffcc00", "#ffffff"])

# Output video settings
video_path = PLASER_DIR / "PLaser_Demonstration.mp4"
fps = 15
width, height = 1280, 720
total_frames = 360  # 24 seconds at 15 FPS

# Initialize OpenCV VideoWriter with HTML5-compatible avc1 (H.264) codec
fourcc = cv2.VideoWriter_fourcc(*'avc1')
video = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))

if not video.isOpened():
    print(f"Error: Failed to open OpenCV VideoWriter for writing at {video_path}")
    sys.exit(1)

print(f"Generating animation simulating the entire UI ({total_frames} frames)...")

# Define Sweep Sequences
# Dashboard Mode: frames 0 to 180
# 3D Cavity Analyzer Mode: frames 180 to 360
r1_seq = np.ones(total_frames) * 0.90
r2_seq = np.ones(total_frames) * 0.05
L_seq = np.ones(total_frames) * 300.0
T0_seq = np.ones(total_frames) * 300.0
I_seq = np.ones(total_frames) * 0.13
w_seq = np.ones(total_frames) * 2.8
d_seq = np.ones(total_frames) * 0.342

# Sweep Ridge Width w (Frames 0 to 15): 2.8 -> 4.0
w_seq[0:15] = np.linspace(2.8, 4.0, 15)
w_seq[15:30] = np.linspace(4.0, 2.8, 15)

# Sweep Active Thickness d (Frames 15 to 30): 0.342 -> 0.15 -> 0.342
d_seq[15:22] = np.linspace(0.342, 0.15, 7)
d_seq[22:30] = np.linspace(0.15, 0.342, 8)

# Sweep R2 (Frames 30 to 80): 0.05 -> 0.45 -> 0.05
r2_seq[30:55] = np.linspace(0.05, 0.45, 25)
r2_seq[55:80] = np.linspace(0.45, 0.05, 25)

# Sweep Current (Frames 80 to 130): 0.13A -> 0.50A -> 0.13A
I_seq[80:105] = np.linspace(0.13, 0.50, 25)
I_seq[105:130] = np.linspace(0.50, 0.13, 25)

# Sweep Temperature (Frames 130 to 180): 300K -> 360K -> 300K
T0_seq[130:155] = np.linspace(300.0, 360.0, 25)
T0_seq[155:180] = np.linspace(360.0, 300.0, 25)

# z-Slice selection sequence for Analyzer Mode (Frames 180 to 360)
# z sweeps: 300um -> 0um (frames 200 to 275) -> 300um (frames 275 to 350)
z_seq = np.ones(total_frames) * 300.0
z_seq[200:275] = np.linspace(300.0, 0.0, 75)
z_seq[275:350] = np.linspace(0.0, 300.0, 75)

# Setup Matplotlib Figure mimicking the Streamlit dark theme
plt.style.use('dark_background')
fig = plt.figure(figsize=(16, 9), facecolor="#0d1117")

# Sidebar axes (left dashboard)
ax_sidebar = fig.add_axes([0, 0, 0.22, 1.0], facecolor="#161b22")
ax_sidebar.axis("off")

# Dashboard viewports (visible in dashboard mode)
ax_carrier = fig.add_axes([0.25, 0.50, 0.22, 0.28], facecolor="#172a45")
ax_optical = fig.add_axes([0.25, 0.14, 0.22, 0.28], facecolor="#172a45")

ax_trans_mode = fig.add_axes([0.49, 0.50, 0.22, 0.28], facecolor="#172a45")
ax_trans_temp = fig.add_axes([0.49, 0.14, 0.22, 0.28], facecolor="#172a45")

ax_horiz_mode = fig.add_axes([0.73, 0.50, 0.22, 0.28], facecolor="#172a45")
ax_vert_mode = fig.add_axes([0.73, 0.14, 0.22, 0.28], facecolor="#172a45")

# 3D Analyzer viewports (visible in analyzer mode)
ax_m2d_z = fig.add_axes([0.25, 0.50, 0.33, 0.28], facecolor="#172a45")
ax_t2d_z = fig.add_axes([0.61, 0.50, 0.33, 0.28], facecolor="#172a45")

ax_3d_m = fig.add_axes([0.25, 0.10, 0.33, 0.28], projection="3d", facecolor="#0d1117")
ax_3d_t = fig.add_axes([0.61, 0.10, 0.33, 0.28], projection="3d", facecolor="#0d1117")

# Grids and coordinates
z_grid_percent = np.linspace(0, 100, 51)
tx = np.linspace(-3.5, 3.5, 40)
ty = np.linspace(-2.0, 2.0, 40)
TX, TY = np.meshgrid(tx, ty)

def write_frame_to_video():
    fig.canvas.draw()
    try:
        if hasattr(fig.canvas, 'buffer_rgba'):
            img = np.asarray(fig.canvas.buffer_rgba())
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        else:
            img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    except Exception:
        img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
    img_bgr = cv2.resize(img_bgr, (width, height))
    video.write(img_bgr)

# Render Loop
for frame in range(total_frames):
    # Determine mode
    mode = "dashboard" if frame < 180 else "analyzer"
    
    # Toggle axes visibility based on mode
    dash_visible = (mode == "dashboard")
    for ax in [ax_carrier, ax_optical, ax_trans_mode, ax_trans_temp, ax_horiz_mode, ax_vert_mode]:
        ax.set_visible(dash_visible)
    for ax in [ax_m2d_z, ax_t2d_z, ax_3d_m, ax_3d_t]:
        ax.set_visible(not dash_visible)

    # Get sweep parameters
    r1 = r1_seq[frame]
    r2 = r2_seq[frame]
    L = L_seq[frame]
    T0 = T0_seq[frame]
    I_active = I_seq[frame]
    w_active = w_seq[frame]
    d_active = d_seq[frame]
    
    # Run PINN prediction
    res = surrogate.predict(
        R1=r1,
        R2=r2,
        L_um=L,
        T0=T0,
        I_active=I_active,
        w_active_um=w_active,
        d_active_um=d_active
    )
    
    P_opt = res["P_opt"]
    P_opt_mw = P_opt * 1000.0
    WPE_pct = res["wpe"] * 100.0
    I_total = res["I_total"]
    N_prof = res["N"]
    P_prof = res["P"]
    z_grid = res["z_grid"]
    
    # Get local slice coordinates
    z_sel = z_seq[frame]
    idx = int(np.clip(round(z_sel / (L / 50.0)), 0, 50))
    
    # State logic based on model predictions
    status = "Inactive"
    color_status = "#ff3366"
    if P_opt_mw > 0.1:
        if WPE_pct > 1.0:
            status = "Optimized Lasing"
            color_status = "#00ffcc"
        elif T0 > 325:
            status = "Thermal Droop"
            color_status = "#ffaa00"
        else:
            status = "Near Threshold"
            color_status = "#58a6ff"
    else:
        status = "Below Threshold"
        color_status = "#8b949e"

    # 1. DRAW SIDEBAR (LEFT DASHBOARD)
    ax_sidebar.clear()
    ax_sidebar.axis("off")
    ax_sidebar.set_facecolor("#161b22")
    # Draw right border line
    ax_sidebar.axvline(x=0.99, color="#30363d", linewidth=1.5)
    
    # App logo and title (Clean ASCII/plain text to avoid missing glyph square box warnings in Matplotlib)
    ax_sidebar.text(0.08, 0.94, "PLaser Designer", color="#58a6ff", fontsize=15, fontweight="bold")
    
    # View Mode Radio Selector
    ax_sidebar.text(0.08, 0.89, "View Mode", color="#8b949e", fontsize=9, fontweight="bold")
    
    dash_active = (mode == "dashboard")
    ax_sidebar.text(0.08, 0.85, "(o)" if dash_active else "( )", color="#58a6ff" if dash_active else "#8b949e", fontsize=10, fontweight="bold")
    ax_sidebar.text(0.18, 0.85, "Multi-Physics Dashboard", color="#c9d1d9" if dash_active else "#8b949e", fontsize=8.5, fontweight="bold" if dash_active else "normal")
    
    ax_sidebar.text(0.08, 0.81, "(o)" if not dash_active else "( )", color="#58a6ff" if not dash_active else "#8b949e", fontsize=10, fontweight="bold")
    ax_sidebar.text(0.18, 0.81, "3D Cavity Field Analyzer", color="#c9d1d9" if not dash_active else "#8b949e", fontsize=8.5, fontweight="bold" if not dash_active else "normal")
    
    ax_sidebar.plot([0.08, 0.92], [0.77, 0.77], color="#30363d", lw=1)
    
    if dash_active:
        # Title: Design Parameters
        ax_sidebar.text(0.08, 0.73, "Design Parameters", color="#58a6ff", fontsize=11, fontweight="bold")
        
        # Helper to draw a slider widget
        def draw_slider(y, label, val_str, fraction):
            ax_sidebar.text(0.08, y + 0.02, label, color="#c9d1d9", fontsize=8)
            ax_sidebar.text(0.92, y + 0.02, val_str, color="#8b949e", fontsize=8, ha="right")
            ax_sidebar.plot([0.08, 0.92], [y, y], color="#30363d", lw=3)
            ax_sidebar.plot([0.08, 0.08 + 0.84 * fraction], [y, y], color="#58a6ff", lw=3)
            ax_sidebar.plot(0.08 + 0.84 * fraction, y, marker="o", color="#58a6ff", ms=6)

        r1_frac = (r1 - 0.1) / (0.95 - 0.1)
        draw_slider(0.70, "Left Mirror R1 (HR)", f"{r1:.2f}", r1_frac)
        
        r2_frac = (r2 - 0.05) / (0.50 - 0.05)
        draw_slider(0.65, "Right Mirror R2 (AR)", f"{r2:.2f}", r2_frac)
        
        L_frac = (L - 100) / (1000 - 100)
        draw_slider(0.60, "Cavity Length L (um)", f"{L:.0f}", L_frac)
        
        # Geometry sliders
        w_frac = (w_active - 1.5) / (4.0 - 1.5)
        draw_slider(0.54, "Active Width w (um)", f"{w_active:.2f}", w_frac)
        
        d_frac = (d_active - 0.10) / (0.50 - 0.10)
        draw_slider(0.48, "Active Thickness d (um)", f"{d_active:.3f}", d_frac)
        
        # Operating Conditions header
        ax_sidebar.text(0.08, 0.41, "Operating Conditions", color="#58a6ff", fontsize=11, fontweight="bold")
        
        T0_frac = (T0 - 250) / (360 - 250)
        draw_slider(0.35, "Ambient Temperature T0 (K)", f"{T0:.0f}", T0_frac)
        
        I_frac = (I_active - 0.01) / (0.50 - 0.01)
        draw_slider(0.29, "Injection Current (A)", f"{I_active:.2f}", I_frac)
        
        # Metrics cards
        rect = plt.Rectangle((0.08, 0.03), 0.84, 0.21, facecolor="#1f242c", edgecolor="#30363d", lw=1, transform=ax_sidebar.transData)
        ax_sidebar.add_patch(rect)
        
        ax_sidebar.text(0.12, 0.19, f"State: {status}", color=color_status, fontsize=8.5, fontweight="bold")
        ax_sidebar.text(0.12, 0.14, f"Output Power: {P_opt_mw:.1f} mW", color="#c9d1d9", fontsize=8.5)
        ax_sidebar.text(0.12, 0.09, f"WPE: {WPE_pct:.2f} %", color="#c9d1d9", fontsize=8.5)
        ax_sidebar.text(0.12, 0.04, f"Total Current: {I_total:.3f} A", color="#c9d1d9", fontsize=8.5)
        
    else:
        # Title: 3D Cavity Controller
        ax_sidebar.text(0.08, 0.73, "3D Cavity Controller", color="#58a6ff", fontsize=11, fontweight="bold")
        
        z_frac = z_sel / L
        # Draw z slider
        ax_sidebar.text(0.08, 0.67, "Inspect Cavity Position z (um)", color="#c9d1d9", fontsize=8)
        ax_sidebar.text(0.92, 0.67, f"{z_sel:.1f}", color="#8b949e", fontsize=8, ha="right")
        ax_sidebar.plot([0.08, 0.92], [0.65, 0.65], color="#30363d", lw=3)
        ax_sidebar.plot([0.08, 0.08 + 0.84 * z_frac], [0.65, 0.65], color="#58a6ff", lw=3)
        ax_sidebar.plot(0.08 + 0.84 * z_frac, 0.65, marker="o", color="#58a6ff", ms=6)
        
        # Metric card
        rect = plt.Rectangle((0.08, 0.32), 0.84, 0.26, facecolor="#1f242c", edgecolor="#30363d", lw=1, transform=ax_sidebar.transData)
        ax_sidebar.add_patch(rect)
        
        ax_sidebar.text(0.12, 0.53, f"Local z Position: {z_sel:.1f} um", color="#58a6ff", fontsize=8.5, fontweight="bold")
        ax_sidebar.text(0.12, 0.46, f"Local Carrier Density N(z):", color="#8b949e", fontsize=7.5)
        ax_sidebar.text(0.12, 0.42, f"{N_prof[idx] / 1e18:.3f} x 10^18 cm^-3", color="#ff7b72", fontsize=9, fontweight="bold")
        ax_sidebar.text(0.12, 0.37, f"Local Optical Power P(z):", color="#8b949e", fontsize=7.5)
        ax_sidebar.text(0.12, 0.33, f"{P_prof[idx] * 1000.0:.1f} mW", color="#64ffda", fontsize=9, fontweight="bold")

    # 2. DRAW RIGHT MAIN PANEL CONTENT
    # Clear labels from previous frames
    fig.texts.clear()
    
    # Title headers in main area
    fig.text(0.25, 0.94, "PLaser Designer", color="#58a6ff", fontsize=18, fontweight="bold")
    fig.text(0.25, 0.91, "Multi-Physics Dashboard" if dash_visible else "3D Cavity Field Analyzer", color="#8b949e", fontsize=10)
    fig.text(0.95, 0.94, f"Frame {frame+1}/{total_frames}", color="#8b949e", fontsize=9, ha="right")
    
    norm_power = max(0.001, P_opt_mw / 250.0)
    
    if dash_visible:
        # Plot 1: Carrier Density N(z)
        ax_carrier.clear()
        ax_carrier.plot(z_grid, N_prof / 1e18, color="#ff7b72", linewidth=2.0)
        ax_carrier.set_title("Carrier Density N(z)", color="white", fontsize=9, fontweight="bold")
        ax_carrier.set_xlabel("z Position (um)", color="#8b949e", fontsize=7.5)
        ax_carrier.set_ylabel("N (10^18 cm^-3)", color="#8b949e", fontsize=7.5)
        ax_carrier.grid(True, linestyle="--", alpha=0.3, color="#233554")
        ax_carrier.tick_params(colors="#8b949e", labelsize=7.5)
        for spine in ax_carrier.spines.values():
            spine.set_color("#30363d")
        
        # Plot 2: Optical Power P(z)
        ax_optical.clear()
        ax_optical.plot(z_grid, P_prof * 1000.0, color="#64ffda", linewidth=2.0)
        ax_optical.set_title("Optical Power Profile P(z)", color="white", fontsize=9, fontweight="bold")
        ax_optical.set_xlabel("z Position (um)", color="#8b949e", fontsize=7.5)
        ax_optical.set_ylabel("Power (mW)", color="#8b949e", fontsize=7.5)
        ax_optical.grid(True, linestyle="--", alpha=0.3, color="#233554")
        ax_optical.tick_params(colors="#8b949e", labelsize=7.5)
        for spine in ax_optical.spines.values():
            spine.set_color("#30363d")
            
        # Plot 3: 2D Mode intensity
        w_waist = 1.5 * (w_active / 2.8)
        d_waist = 0.5 * (d_active / 0.342)
        w_thermal = 2.0 * (w_active / 2.8)
        
        ax_trans_mode.clear()
        I_mode = 0.3 * norm_power * np.exp(-TX**2 / w_waist**2 - TY**2 / d_waist**2)
        ax_trans_mode.contourf(TX, TY, I_mode, levels=15, cmap=cmap_mode, vmin=0, vmax=0.36)
        ax_trans_mode.set_title("Mode Intensity Shape |Psi|^2", color="white", fontsize=9, fontweight="bold")
        ax_trans_mode.set_xlabel("x width (um)", color="#8b949e", fontsize=7.5)
        ax_trans_mode.set_ylabel("y height (um)", color="#8b949e", fontsize=7.5)
        ax_trans_mode.tick_params(colors="#8b949e", labelsize=7.5)
        for spine in ax_trans_mode.spines.values():
            spine.set_color("#30363d")
        rect = plt.Rectangle((-w_active/2.0, -d_active/2.0), w_active, d_active, fill=False, edgecolor="#ffffff", linestyle=":", alpha=0.5)
        ax_trans_mode.add_patch(rect)
        ax_trans_mode.text(0, -d_active/2.0 - 0.3, f"Active Region ({w_active:.1f} x {d_active:.3f} um)", color="white", fontsize=6.5, ha="center", alpha=0.7)
        
        # Plot 4: 2D Temperature heat map
        ax_trans_temp.clear()
        heating_power = max(0.0, I_total * 1.05 - P_opt)
        delta_T = 18.0 * heating_power * (T0 / 300.0)**1.5
        T_trans = T0 + delta_T * np.exp(-TX**2 / w_thermal**2) * ((TY + 2.0)/2.0) * np.exp(-TY**2 / 0.8**2)
        ax_trans_temp.contourf(TX, TY, T_trans, levels=15, cmap=cmap_temp, vmin=250.0, vmax=385.0)
        ax_trans_temp.set_title("Temperature Heat Map T(x,y)", color="white", fontsize=9, fontweight="bold")
        ax_trans_temp.set_xlabel("x width (um)", color="#8b949e", fontsize=7.5)
        ax_trans_temp.set_ylabel("y height (um)", color="#8b949e", fontsize=7.5)
        ax_trans_temp.tick_params(colors="#8b949e", labelsize=7.5)
        for spine in ax_trans_temp.spines.values():
            spine.set_color("#30363d")
        ax_trans_temp.axhline(y=-2.0, color="white", linestyle="-", linewidth=1.2, alpha=0.8)
        ax_trans_temp.text(0, -1.8, "Copper Heat Sink Mount (T0)", color="white", fontsize=6.5, ha="center", fontweight="bold")
        
        # Plot 5: Horizontal slice
        ax_horiz_mode.clear()
        I_horiz = 0.3 * norm_power * np.exp(-tx**2 / w_waist**2)
        ax_horiz_mode.plot(tx, I_horiz, color="#ffcc00", linewidth=2.0)
        ax_horiz_mode.set_title("Horizontal Cut Mode Profile", color="white", fontsize=9, fontweight="bold")
        ax_horiz_mode.set_xlabel("x width (um)", color="#8b949e", fontsize=7.5)
        ax_horiz_mode.set_ylabel("Intensity", color="#8b949e", fontsize=7.5)
        ax_horiz_mode.grid(True, linestyle="--", alpha=0.3, color="#233554")
        ax_horiz_mode.tick_params(colors="#8b949e", labelsize=7.5)
        ax_horiz_mode.set_ylim(0.0, 0.36)
        for spine in ax_horiz_mode.spines.values():
            spine.set_color("#30363d")
            
        # Plot 6: Vertical slice
        ax_vert_mode.clear()
        I_vert = 0.3 * norm_power * np.exp(-ty**2 / d_waist**2)
        ax_vert_mode.plot(ty, I_vert, color="#ff33cc", linewidth=2.0)
        ax_vert_mode.set_title("Vertical Cut Mode Profile", color="white", fontsize=9, fontweight="bold")
        ax_vert_mode.set_xlabel("y height (um)", color="#8b949e", fontsize=7.5)
        ax_vert_mode.set_ylabel("Intensity", color="#8b949e", fontsize=7.5)
        ax_vert_mode.grid(True, linestyle="--", alpha=0.3, color="#233554")
        ax_vert_mode.tick_params(colors="#8b949e", labelsize=7.5)
        ax_vert_mode.set_ylim(0.0, 0.36)
        for spine in ax_vert_mode.spines.values():
            spine.set_color("#30363d")
            
        # Draw guidance text box at bottom
        fig.text(0.25, 0.05, "Design Guidance: Mirror asymmetry R1 >> R2 skews the optical profile towards front facet (SHB dip).", color="#8b949e", fontsize=8.5)
        
    else:
        # 3D Cavity Analyzer Mode (Local Slices & 3D Surface plots)
        w_waist_z = 1.5 * (w_active / 2.8)
        d_waist_z = 0.5 * (d_active / 0.342)
        w_thermal = 2.0 * (w_active / 2.8)
        
        ax_m2d_z.clear()
        norm_power_z = max(0.001, P_prof[idx] * 1000.0 / 250.0)
        I_mode_z = 0.3 * norm_power_z * np.exp(-TX**2 / w_waist_z**2 - TY**2 / d_waist_z**2)
        ax_m2d_z.contourf(TX, TY, I_mode_z, levels=15, cmap=cmap_mode, vmin=0, vmax=0.36)
        ax_m2d_z.set_title(f"Local Optical Mode at z = {z_sel:.1f} um", color="white", fontsize=9, fontweight="bold")
        ax_m2d_z.set_xlabel("x width (um)", color="#8b949e", fontsize=7.5)
        ax_m2d_z.set_ylabel("y height (um)", color="#8b949e", fontsize=7.5)
        ax_m2d_z.tick_params(colors="#8b949e", labelsize=7.5)
        for spine in ax_m2d_z.spines.values():
            spine.set_color("#30363d")
        rect = plt.Rectangle((-w_active/2.0, -d_active/2.0), w_active, d_active, fill=False, edgecolor="#ffffff", linestyle=":", alpha=0.5)
        ax_m2d_z.add_patch(rect)
        ax_m2d_z.text(0, -d_active/2.0 - 0.3, f"Active Region ({w_active:.1f} x {d_active:.3f} um)", color="white", fontsize=6.5, ha="center", alpha=0.7)
        
        ax_t2d_z.clear()
        P_avg = max(1e-5, np.mean(P_prof))
        T_scale_z = P_prof[idx] / P_avg
        heating_power = max(0.0, I_total * 1.05 - P_opt)
        delta_T = 18.0 * heating_power * (T0 / 300.0)**1.5
        T_trans_z = T0 + delta_T * T_scale_z * np.exp(-TX**2 / w_thermal**2) * ((TY + 2.0)/2.0) * np.exp(-TY**2 / 0.8**2)
        ax_t2d_z.contourf(TX, TY, T_trans_z, levels=15, cmap=cmap_temp, vmin=250.0, vmax=385.0)
        ax_t2d_z.set_title(f"Local Temperature at z = {z_sel:.1f} um", color="white", fontsize=9, fontweight="bold")
        ax_t2d_z.set_xlabel("x width (um)", color="#8b949e", fontsize=7.5)
        ax_t2d_z.set_ylabel("y height (um)", color="#8b949e", fontsize=7.5)
        ax_t2d_z.tick_params(colors="#8b949e", labelsize=7.5)
        for spine in ax_t2d_z.spines.values():
            spine.set_color("#30363d")
        ax_t2d_z.axhline(y=-2.0, color="white", linestyle="-", linewidth=1.2, alpha=0.8)
        ax_t2d_z.text(0, -1.8, "Copper Heat Sink Mount (T0)", color="white", fontsize=6.5, ha="center", fontweight="bold")
        
        # 3D surface plots (rendered at flat 1.3 height)
        ax_3d_m.clear()
        TX_3d, TZ_3d = np.meshgrid(tx, z_grid)
        I_3d = 0.3 * (P_prof[:, None] * 1000.0 / 250.0) * np.exp(-TX_3d**2 / w_waist_z**2)
        ax_3d_m.plot_surface(TX_3d, TZ_3d, I_3d, cmap=cmap_mode, edgecolor="none", antialiased=True, vmin=0, vmax=0.36)
        ax_3d_m.set_title("3D Optical Intensity |Psi(x, 0, z)|^2", color="white", fontsize=9.5, fontweight="bold")
        ax_3d_m.set_xlabel("x width (um)", color="#8b949e", fontsize=7)
        ax_3d_m.set_ylabel("z Position (um)", color="#8b949e", fontsize=7)
        ax_3d_m.set_zlabel("Intensity", color="#8b949e", fontsize=7)
        ax_3d_m.set_box_aspect((1.5, 1.0, 0.45))
        ax_3d_m.view_init(elev=20, azim=-55)
        ax_3d_m.xaxis.set_pane_color((0.09, 0.16, 0.27, 1.0))
        ax_3d_m.yaxis.set_pane_color((0.09, 0.16, 0.27, 1.0))
        ax_3d_m.zaxis.set_pane_color((0.09, 0.16, 0.27, 1.0))
        ax_3d_m.tick_params(colors="#8b949e", labelsize=6.5)
        
        ax_3d_t.clear()
        T_3d = T0 + delta_T * (P_prof[:, None] / P_avg) * np.exp(-TX_3d**2 / w_thermal**2)
        ax_3d_t.plot_surface(TX_3d, TZ_3d, T_3d, cmap=cmap_temp, edgecolor="none", antialiased=True, vmin=250.0, vmax=385.0)
        ax_3d_t.set_title("3D Temperature Profile T(x, 0, z)", color="white", fontsize=9.5, fontweight="bold")
        ax_3d_t.set_xlabel("x width (um)", color="#8b949e", fontsize=7)
        ax_3d_t.set_ylabel("z Position (um)", color="#8b949e", fontsize=7)
        ax_3d_t.set_zlabel("Temp (K)", color="#8b949e", fontsize=7)
        ax_3d_t.set_box_aspect((1.5, 1.0, 0.45))
        ax_3d_t.view_init(elev=20, azim=-55)
        ax_3d_t.xaxis.set_pane_color((0.09, 0.16, 0.27, 1.0))
        ax_3d_t.yaxis.set_pane_color((0.09, 0.16, 0.27, 1.0))
        ax_3d_t.zaxis.set_pane_color((0.09, 0.16, 0.27, 1.0))
        ax_3d_t.tick_params(colors="#8b949e", labelsize=6.5)

    write_frame_to_video()
    
    if (frame + 1) % 60 == 0:
        print(f"Rendered {frame+1}/{total_frames} frames...")

# Cleanup
video.release()
plt.close(fig)
print(f"Animation successfully saved to {video_path}")
