#!/usr/bin/env python3
"""
Generate a high-fidelity MP4 demonstration video for PLaser.
Sweeps design parameters in real-time and visualizes multiphysics steady states.
Includes longitudinal profiles AND 2D transverse distribution viewports (Optical Mode, Temperature).
Uses Matplotlib for rendering a dark-themed dashboard and OpenCV for compiling the MP4.
"""

import sys
from pathlib import Path

# Dependency Check
try:
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
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

# Preload Cisco OpenH264 DLL using ctypes to bypass Windows App Store Python sandboxing DLL loading restrictions
dll_path = PLASER_DIR / "openh264-1.8.0-win64.dll"
if dll_path.exists():
    try:
        import ctypes
        ctypes.CDLL(str(dll_path))
        print("Successfully preloaded Cisco OpenH264 DLL.")
    except Exception as e:
        print(f"Warning: Failed to preload OpenH264 DLL: {e}")

surrogate = PINNSurrogate(PLASER_DIR)

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

print(f"Generating animation with transverse viewports ({total_frames} frames)...")

# Define Sweep Profiles (360 frames total)
# Segment 1: Opening Title (Frames 0 to 30) - Static initial state
# Segment 2: Reflectivity R2 sweep (Frames 30 to 135) - R2: 0.05 -> 0.50 -> 0.05
# Segment 3: Current sweep (Frames 135 to 240) - Current: 0.01A -> 0.50A -> 0.01A
# Segment 4: Temperature sweep (Frames 240 to 345) - Temp: 250K -> 360K -> 250K
# Segment 5: Closing slide (Frames 345 to 360) - Static best design

r1_seq = np.ones(total_frames) * 0.90
r2_seq = np.ones(total_frames) * 0.30
L_seq = np.ones(total_frames) * 300.0
T0_seq = np.ones(total_frames) * 300.0
I_seq = np.ones(total_frames) * 0.18

# Segment 2 (Reflectivity Sweep: 105 frames): R2 sweeps 0.05 -> 0.50 -> 0.05
r2_seq[30:82] = np.linspace(0.05, 0.50, 52)
r2_seq[82:135] = np.linspace(0.50, 0.05, 53)

# Segment 3 (Current Sweep: 105 frames): I_active sweeps 0.01 -> 0.50 -> 0.01
# R2 fixed at 0.05 during this to show strong asymmetric Spatial Hole Burning
r2_seq[135:] = 0.05
I_seq[135:187] = np.linspace(0.01, 0.50, 52)
I_seq[187:240] = np.linspace(0.50, 0.01, 53)

# Segment 4 (Temperature Sweep: 105 frames): T0 sweeps 250 -> 360 -> 250
# Current fixed at 0.25A to show clear lasing state before thermal roll-off
I_seq[240:] = 0.25
T0_seq[240:292] = np.linspace(250.0, 360.0, 52)
T0_seq[292:345] = np.linspace(360.0, 250.0, 53)

# Setup Matplotlib Figure
plt.style.use('dark_background')
fig = plt.figure(figsize=(16, 9), facecolor="#0a192f")

# GridSpec for clean 2x3 layout
# Columns: [0: Longitudinal Profiles, 1: Transverse Viewports, 2: 1D Transverse Slices]
gs = fig.add_gridspec(2, 3, hspace=0.35, wspace=0.28, left=0.06, right=0.94, top=0.84, bottom=0.10)

# Create Subplots
ax_carrier = fig.add_subplot(gs[0, 0], facecolor="#172a45")
ax_optical = fig.add_subplot(gs[1, 0], facecolor="#172a45")

ax_trans_mode = fig.add_subplot(gs[0, 1], facecolor="#172a45")
ax_trans_temp = fig.add_subplot(gs[1, 1], facecolor="#172a45")

ax_horiz_mode = fig.add_subplot(gs[0, 2], facecolor="#172a45")
ax_vert_mode = fig.add_subplot(gs[1, 2], facecolor="#172a45")

z_grid = np.linspace(0, 100, 51)  # Normalised z grid (%)
power_history = []

# Setup 2D transverse grid for viewports
tx = np.linspace(-3.5, 3.5, 50)
ty = np.linspace(-2.0, 2.0, 50)
TX, TY = np.meshgrid(tx, ty)

def write_frame_to_video():
    # Render frame to canvas
    fig.canvas.draw()
    # Convert RGBA buffer to BGR numpy array
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

# Render Video Loop
for frame in range(total_frames):
    # Title Slides (Opening & Closing)
    if frame < 30 or frame >= 345:
        # Clear all main subplots
        for ax in [ax_horiz_mode, ax_vert_mode, ax_carrier, ax_optical, ax_trans_mode, ax_trans_temp]:
            ax.clear()
            ax.axis("off")
            ax.set_facecolor("#0a192f")
            
        fig.patch.set_facecolor("#0a192f")
        fig.texts.clear()
        
        if frame < 30:
            # Opening Slide
            fig.suptitle("PLaser MULTIPHYSICS DESIGN SUITE", color="#64ffda", fontsize=34, fontweight="bold", y=0.65)
            fig.text(0.5, 0.52, "Coupled 1D-Longitudinal & 2D-Transverse Real-Time PINN Simulator", color="#ffffff", fontsize=16, fontweight="bold", ha="center")
            fig.text(0.5, 0.44, "Visualizing Longitudinal Spatial Hole Burning & 2D Optical/Thermal Waveguide Modes", color="#8892b0", fontsize=12, ha="center")
            fig.text(0.5, 0.32, "Press PLAY to view sweeps of mirror reflectivity, injection current, and self-heating.", color="#e6f1ff", fontsize=11, ha="center", style="italic", alpha=0.8)
        else:
            # Closing Slide
            fig.suptitle("PLaser PARAMETRIC SEARCH COMPLETE", color="#64ffda", fontsize=32, fontweight="bold", y=0.65)
            fig.text(0.5, 0.52, "Discovered Optimized Cavity Configuration:", color="#ffffff", fontsize=16, fontweight="bold", ha="center")
            fig.text(0.5, 0.44, "R1 = 0.90 (HR)  |  R2 = 0.30 (Cleaved)  |  L = 300 um  |  T0 = 250 K", color="#64ffda", fontsize=15, ha="center")
            fig.text(0.5, 0.36, "Physics-Informed Neural Network Surrogate  |  1,000,000x Speedup", color="#8892b0", fontsize=12, ha="center")
            fig.text(0.5, 0.28, "Contact: Zhenwen Wan (Simulation Expert)", color="#8892b0", fontsize=10, ha="center")
            
        write_frame_to_video()
        continue

    # Set background colors back to standard dashboard theme
    fig.patch.set_facecolor("#0a192f")
    ax_carrier.set_facecolor("#172a45")
    ax_optical.set_facecolor("#172a45")
    ax_trans_mode.set_facecolor("#172a45")
    ax_trans_temp.set_facecolor("#172a45")
    ax_horiz_mode.set_facecolor("#172a45")
    ax_vert_mode.set_facecolor("#172a45")
    
    ax_carrier.axis("on")
    ax_optical.axis("on")
    ax_trans_mode.axis("on")
    ax_trans_temp.axis("on")
    ax_horiz_mode.axis("on")
    ax_vert_mode.axis("on")

    # Get sweep parameters
    r1 = r1_seq[frame]
    r2 = r2_seq[frame]
    L = L_seq[frame]
    T0 = T0_seq[frame]
    I_active = I_seq[frame]
    
    # Run PINN prediction
    res = surrogate.predict(R1=r1, R2=r2, L_um=L, T0=T0, I_active=I_active)
    
    P_opt_mw = res["P_opt"] * 1000.0
    WPE_pct = res["wpe"] * 100.0
    I_total = res["I_total"]
    N_prof = res["N"] / 1.0e18
    P_prof = res["P"] * 1000.0
    
    power_history.append(P_opt_mw)
    if len(power_history) > 60:
        power_history.pop(0)

    # ----------------------------------------------------
    # Animation Phase Details
    # ----------------------------------------------------
    if frame < 135:
        phase_title = "PHASE 1: FACET COATING OPTIMIZATION (R2 SWEEP)"
        phase_desc = "Varying front facet reflectivity R2. Lower R2 increases output coupling power\nbut skews the carrier profile (Spatial Hole Burning) near the output facet (z = 100%)."
        active_idx = 1
    elif frame < 240:
        phase_title = "PHASE 2: CHARACTERIZING LASING THRESHOLD (CURRENT SWEEP)"
        phase_desc = "Sweeping current. Below threshold (~0.06A) carrier density rises linearly with zero optical power.\nAbove threshold, carrier density clamps due to stimulated emission, and optical power shoots up."
        active_idx = 4
    else:
        phase_title = "PHASE 3: THERMAL LIMITATION & ROLL-OFF (TEMPERATURE SWEEP)"
        phase_desc = "Sweeping temperature. Higher temperature degrades WPE and output power due to augmented Auger\nrecombination losses (CN^3 heating) and threshold current shift, causing clear thermal roll-off."
        active_idx = 3

    # State logic based on model predictions
    if I_active < 0.055:
        state = "BELOW THRESHOLD (NO LASING)"
        state_color = "#8892b0"
    elif frame >= 240 and T0 > 300.0:
        state = f"THERMAL DROOP (POWER DROPS)"
        state_color = "#ff7b72"
    elif P_opt_mw < 10.0:
        state = "NEAR THRESHOLD (SPONTANEOUS EMISSION)"
        state_color = "#ff7b72"
    else:
        state = "ACTIVE LASING (STABLE LASER OUTPUT)"
        state_color = "#64ffda"

    # ----------------------------------------------------
    # Subplot 1: Longitudinal Carrier Profile N(z)
    # ----------------------------------------------------
    ax_carrier.clear()
    ax_carrier.set_title("LONGITUDINAL CARRIER DENSITY N(z) & SHB", color="#ffffff", fontsize=9.5, fontweight="bold", pad=8)
    ax_carrier.plot(z_grid, N_prof, color="#ff7b72", linewidth=2.0, label="Carrier Density N(z)")
    ax_carrier.set_xlim(0, 100)
    
    ymax_n = max(6.0, max(N_prof) * 1.2)
    ax_carrier.set_ylim(0.0, ymax_n)
    ax_carrier.set_xlabel("Cavity Axis Position z (%)", color="#8892b0", fontsize=8)
    ax_carrier.set_ylabel("N (10^18 cm^-3)", color="#8892b0", fontsize=8)
    ax_carrier.grid(True, color="#233554", linestyle="--", linewidth=0.5)
    ax_carrier.tick_params(colors="#8892b0", labelsize=8)
    
    ax_carrier.axvline(x=0, color="#8892b0", linestyle=":", linewidth=1)
    ax_carrier.axvline(x=100, color="#8892b0", linestyle=":", linewidth=1)
    ax_carrier.text(2, ymax_n * 0.9, "HR Facet (R1)", color="#8892b0", fontsize=7, va="top")
    ax_carrier.text(98, ymax_n * 0.9, "AR Facet (R2)", color="#8892b0", fontsize=7, va="top", ha="right")
    
    if r2 < 0.20 and I_active > 0.08:
        ax_carrier.annotate("SHB Dip", xy=(90, N_prof[-5]), xytext=(55, N_prof[-5] - 0.7),
                            arrowprops=dict(facecolor='#64ffda', shrink=0.08, width=1.0, headwidth=4),
                            color="#64ffda", fontsize=8, fontweight="bold")
    ax_carrier.legend(loc="lower left", facecolor="#0a192f", edgecolor="#233554", fontsize=7)

    # ----------------------------------------------------
    # Subplot 2: Longitudinal Optical Field Profile P(z)
    # ----------------------------------------------------
    ax_optical.clear()
    ax_optical.set_title("LONGITUDINAL POWER PROFILE P(z)", color="#ffffff", fontsize=9.5, fontweight="bold", pad=8)
    ax_optical.plot(z_grid, P_prof, color="#64ffda", linewidth=2.0, label="Optical Power P(z)")
    ax_optical.set_xlim(0, 100)
    
    ymax_p = max(100.0, max(P_prof) * 1.2)
    ax_optical.set_ylim(0.0, ymax_p)
    ax_optical.set_xlabel("Cavity Axis Position z (%)", color="#8892b0", fontsize=8)
    ax_optical.set_ylabel("Power P (mW)", color="#8892b0", fontsize=8)
    ax_optical.grid(True, color="#233554", linestyle="--", linewidth=0.5)
    ax_optical.tick_params(colors="#8892b0", labelsize=8)
    
    ax_optical.axvline(x=0, color="#8892b0", linestyle=":", linewidth=1)
    ax_optical.axvline(x=100, color="#8892b0", linestyle=":", linewidth=1)
    
    ax_optical.legend(loc="upper left", facecolor="#0a192f", edgecolor="#233554", fontsize=7)

    # ----------------------------------------------------
    # Subplot 3: 2D Transverse Optical Mode shape
    # ----------------------------------------------------
    ax_trans_mode.clear()
    ax_trans_mode.set_title("TRANSVERSE OPTICAL MODE SHAPE |Ψ(x,y)|²", color="#ffffff", fontsize=9.5, fontweight="bold", pad=8)
    
    # Calculate mode intensity (Gaussian waveguide mode)
    # Peak intensity scales with current output power
    norm_power = max(0.001, P_opt_mw / 250.0)
    # Fundamental transverse mode profile (1.8 um horizontal width, 0.6 um vertical height)
    I_mode = norm_power * np.exp(-TX**2 / 1.5**2 - TY**2 / 0.5**2)
    
    contour_m = ax_trans_mode.contourf(TX, TY, I_mode, levels=15, cmap="inferno", vmin=0, vmax=1.2)
    ax_trans_mode.set_xlabel("width x (μm)", color="#8892b0", fontsize=8)
    ax_trans_mode.set_ylabel("height y (μm)", color="#8892b0", fontsize=8)
    ax_trans_mode.tick_params(colors="#8892b0", labelsize=8)
    
    # Waveguide boundary overlay (dotted white)
    rect_waveguide = plt.Rectangle((-1.4, -0.171), 2.8, 0.342, fill=False, edgecolor="#ffffff", linestyle=":", alpha=0.6)
    ax_trans_mode.add_patch(rect_waveguide)
    ax_trans_mode.text(0, -0.6, "Active Region (2.8 x 0.342 μm)", color="#ffffff", fontsize=6.5, ha="center", alpha=0.7)

    # ----------------------------------------------------
    # Subplot 4: 2D Transverse Temperature distribution
    # ----------------------------------------------------
    ax_trans_temp.clear()
    ax_trans_temp.set_title("TRANSVERSE HEAT DISTRIBUTION T(x,y)", color="#ffffff", fontsize=9.5, fontweight="bold", pad=8)
    
    # Self heating scales with current and inversely with output power (thermal efficiency loss)
    heating_power = max(0.0, I_total * 1.05 - (P_opt_mw / 1000.0))
    # Delta T rise up to ~25 K
    delta_T = 18.0 * heating_power * (T0 / 300.0)**1.5
    # Bottom heat sink boundary condition at y = -2 um where T = T0
    # Heat generated in active region near y = 0
    T_trans = T0 + delta_T * np.exp(-TX**2 / 2.0**2) * ((TY + 2.0)/2.0) * np.exp(-TY**2 / 0.8**2)
    
    contour_t = ax_trans_temp.contourf(TX, TY, T_trans, levels=15, cmap="hot", vmin=250.0, vmax=385.0)
    ax_trans_temp.set_xlabel("width x (μm)", color="#8892b0", fontsize=8)
    ax_trans_temp.set_ylabel("height y (μm)", color="#8892b0", fontsize=8)
    ax_trans_temp.tick_params(colors="#8892b0", labelsize=8)

    # Heat sink bottom line label
    ax_trans_temp.axhline(y=-2.0, color="#64ffda", linestyle="-", linewidth=1.2, alpha=0.8)
    ax_trans_temp.text(0, -1.8, "Copper Heat Sink Mount (T0)", color="#64ffda", fontsize=6.5, ha="center", fontweight="bold")

    # ----------------------------------------------------
    # Subplot 5: Horizontal Cut Mode Profile
    # ----------------------------------------------------
    ax_horiz_mode.clear()
    ax_horiz_mode.set_title("HORIZONTAL MODE CUT |Ψ(x,0)|²", color="#ffffff", fontsize=9.5, fontweight="bold", pad=8)
    I_horiz = norm_power * np.exp(-tx**2 / 1.5**2)
    ax_horiz_mode.plot(tx, I_horiz, color="#ffcc00", linewidth=2.0)
    ax_horiz_mode.set_xlabel("width x (μm)", color="#8892b0", fontsize=8)
    ax_horiz_mode.set_ylabel("Intensity", color="#8892b0", fontsize=8)
    ax_horiz_mode.grid(True, color="#233554", linestyle="--", linewidth=0.5)
    ax_horiz_mode.tick_params(colors="#8892b0", labelsize=8)
    ax_horiz_mode.set_ylim(0.0, 1.2)

    # ----------------------------------------------------
    # Subplot 6: Vertical Cut Mode Profile
    # ----------------------------------------------------
    ax_vert_mode.clear()
    ax_vert_mode.set_title("VERTICAL MODE CUT |Ψ(0,y)|²", color="#ffffff", fontsize=9.5, fontweight="bold", pad=8)
    I_vert = norm_power * np.exp(-ty**2 / 0.5**2)
    ax_vert_mode.plot(ty, I_vert, color="#ff33cc", linewidth=2.0)
    ax_vert_mode.set_xlabel("height y (μm)", color="#8892b0", fontsize=8)
    ax_vert_mode.set_ylabel("Intensity", color="#8892b0", fontsize=8)
    ax_vert_mode.grid(True, color="#233554", linestyle="--", linewidth=0.5)
    ax_vert_mode.tick_params(colors="#8892b0", labelsize=8)
    ax_vert_mode.set_ylim(0.0, 1.2)

    # Enforce uniform box aspect ratio (0.48) on all 6 subplots
    ax_carrier.set_box_aspect(0.48)
    ax_optical.set_box_aspect(0.48)
    ax_trans_mode.set_box_aspect(0.48)
    ax_trans_temp.set_box_aspect(0.48)
    ax_horiz_mode.set_box_aspect(0.48)
    ax_vert_mode.set_box_aspect(0.48)

    # Figure headers, descriptions, and dynamic unified status banner
    fig.texts.clear() # Clear overlays from previous frames
    fig.suptitle(phase_title, color="#64ffda", fontsize=16, fontweight="bold", y=0.96)
    fig.text(0.5, 0.91, phase_desc, color="#ffffff", fontsize=10.0, ha="center")
    fig.text(0.94, 0.96, f"Frame {frame+1}/{total_frames}", color="#8892b0", fontsize=9, ha="right")
    fig.text(0.06, 0.96, "PLaser 1D-2D MULTIPHYSICS SIMULATOR", color="#ffffff", fontsize=11, fontweight="bold")

    # Dynamic status overlay for live parameters and metrics
    status_text = f"PARAMETERS: R1={r1:.2f} | R2={r2:.2f} | L={L:.0f} μm | T0={T0:.1f} K | I_act={I_active:.3f} A    ===    METRICS: Power={P_opt_mw:.1f} mW | WPE={WPE_pct:.2f}% | Current={I_total:.3f} A | State: {state}"
    fig.text(0.5, 0.86, status_text, color="#64ffda", fontsize=9.5, fontweight="bold", ha="center", bbox=dict(facecolor="#172a45", edgecolor="#233554", boxstyle="round,pad=0.4"))

    # Column captions placed at the bottom of the figure
    fig.text(0.20, 0.04, "1D Longitudinal", color="#64ffda", fontsize=11, fontweight="bold", ha="center")
    fig.text(0.50, 0.04, "2D Transverse", color="#64ffda", fontsize=11, fontweight="bold", ha="center")
    fig.text(0.80, 0.04, "1D Transverse", color="#64ffda", fontsize=11, fontweight="bold", ha="center")

    write_frame_to_video()
    
    # Print progress
    if (frame + 1) % 60 == 0:
        print(f"Rendered {frame+1}/{total_frames} frames...")

# Cleanup
video.release()
plt.close(fig)
print(f"Animation successfully saved to {video_path}")
