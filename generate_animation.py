#!/usr/bin/env python3
"""
Generate a high-fidelity MP4 demonstration video for PLaser.
Sweeps design parameters in real-time and visualizes multiphysics steady states.
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
surrogate = PINNSurrogate(PLASER_DIR)

# Output video settings
video_path = PLASER_DIR / "PLaser_Demonstration.mp4"
fps = 15
width, height = 1280, 720
total_frames = 360  # 24 seconds at 15 FPS

# Initialize OpenCV VideoWriter
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video = cv2.VideoWriter(str(video_path), fourcc, fps, (width, height))

if not video.isOpened():
    print(f"Error: Failed to open OpenCV VideoWriter for writing at {video_path}")
    sys.exit(1)

print(f"Generating animation ({total_frames} frames)...")

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
# GridSpec for clean layout
gs = fig.add_gridspec(2, 2, hspace=0.32, wspace=0.25, left=0.06, right=0.94, top=0.88, bottom=0.08)

# Create Subplots
ax_params = fig.add_subplot(gs[0, 0], facecolor="#172a45")
ax_metrics = fig.add_subplot(gs[0, 1], facecolor="#172a45")
ax_carrier = fig.add_subplot(gs[1, 0], facecolor="#172a45")
ax_optical = fig.add_subplot(gs[1, 1], facecolor="#172a45")
ax_mini = fig.add_axes([0.77, 0.58, 0.15, 0.10], facecolor="#0a192f")

z_grid = np.linspace(0, 100, 51)  # Normalised z grid (%)
power_history = []

def write_frame_to_video():
    # Render frame to canvas
    fig.canvas.draw()
    # Convert RGBA buffer to BGR numpy array
    try:
        # Compatibility check for matplotlib version
        if hasattr(fig.canvas, 'buffer_rgba'):
            img = np.asarray(fig.canvas.buffer_rgba())
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        else:
            img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
            img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
            img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    except Exception:
        # Fallback buffer extraction
        img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
    img_bgr = cv2.resize(img_bgr, (width, height))
    video.write(img_bgr)

# Render Video Loop
for frame in range(total_frames):
    # ----------------------------------------------------
    # Title Slides (Opening & Closing)
    # ----------------------------------------------------
    if frame < 30 or frame >= 345:
        # Clear main subplots
        for ax in [ax_params, ax_metrics, ax_carrier, ax_optical, ax_mini]:
            ax.clear()
            ax.axis("off")
            ax.set_facecolor("#0a192f")
            
        fig.patch.set_facecolor("#0a192f")
        
        if frame < 30:
            # Opening Slide
            fig.suptitle("PLaser DESIGN SUITE", color="#64ffda", fontsize=38, fontweight="bold", y=0.65)
            fig.text(0.5, 0.52, "Physics-Informed Neural Network (PINN) Surrogate Model", color="#ffffff", fontsize=18, fontweight="bold", ha="center")
            fig.text(0.5, 0.44, "Real-Time Diode Laser Multi-Physics EDA Sweeps  |  Latency < 5 ms", color="#8892b0", fontsize=13, ha="center")
            fig.text(0.5, 0.32, "Press PLAY to view sweeps of Mirror Reflectivity, Injection Current, and Temperature.", color="#e6f1ff", fontsize=11, ha="center", style="italic", alpha=0.8)
        else:
            # Closing Slide
            fig.suptitle("PLaser OPTIMIZATION COMPLETE", color="#64ffda", fontsize=34, fontweight="bold", y=0.65)
            fig.text(0.5, 0.52, "Optimal Cavity Configuration Discovered:", color="#ffffff", fontsize=16, fontweight="bold", ha="center")
            fig.text(0.5, 0.44, "R1 = 0.90 (HR)  |  R2 = 0.30 (Cleaved)  |  Length = 300 um  |  Temp = 250 K", color="#64ffda", fontsize=15, ha="center")
            fig.text(0.5, 0.36, "AI-Driven Simulation Platform  |  Collaborators Welcome", color="#8892b0", fontsize=12, ha="center")
            fig.text(0.5, 0.28, "Contact: Zhenwen Wan (AI + Simulation Expert)", color="#8892b0", fontsize=10, ha="center")
            
        write_frame_to_video()
        continue

    # Set background colors back to standard dashboard theme
    fig.patch.set_facecolor("#0a192f")
    ax_params.set_facecolor("#172a45")
    ax_metrics.set_facecolor("#172a45")
    ax_carrier.set_facecolor("#172a45")
    ax_optical.set_facecolor("#172a45")
    ax_params.axis("on")
    ax_metrics.axis("on")
    ax_carrier.axis("on")
    ax_optical.axis("on")

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
        # Detect droop: check if current power is lower than the peak power at T0=250K
        state = f"THERMAL DROOP (POWER DROPS)"
        state_color = "#ff7b72"
    elif P_opt_mw < 10.0:
        state = "NEAR THRESHOLD (SPONTANEOUS EMISSION)"
        state_color = "#ff7b72"
    else:
        state = "ACTIVE LASING (STABLE LASER OUTPUT)"
        state_color = "#64ffda"

    # ----------------------------------------------------
    # Subplot 1: Design Parameters
    # ----------------------------------------------------
    ax_params.clear()
    ax_params.set_title("LIVE PARAMETER CONTROLS", color="#ffffff", fontsize=11, fontweight="bold", pad=12)
    ax_params.set_xlim(0, 100)
    ax_params.set_ylim(-0.5, 4.5)
    ax_params.axis("off")
    
    labels = [
        f"Rear Facet Reflectivity (R1): {r1:.2f}",
        f"Front Facet Reflectivity (R2): {r2:.2f}",
        f"Cavity Length (L): {L:.0f} um",
        f"Operating Temp (T0): {T0:.1f} K",
        f"Active Current (I_act): {I_active:.3f} A"
    ]
    # Parameter values mapped to 0-100% of progress bars
    vals_pct = [
        (r1 - 0.70) / 0.25 * 100.0,
        (r2 - 0.05) / 0.45 * 100.0,
        (L - 100.0) / 900.0 * 100.0,
        (T0 - 250.0) / 110.0 * 100.0,
        (I_active - 0.01) / 0.49 * 100.0
    ]
    
    for i in range(5):
        # Draw background bar
        rect_bg = plt.Rectangle((28, i - 0.15), 65, 0.3, facecolor="#0a192f", edgecolor="#233554")
        ax_params.add_patch(rect_bg)
        # Draw active bar (highlight current swept parameter)
        color = "#64ffda" if i == active_idx else "#8892b0"
        if i == 3 and T0 > 300.0:
            color = "#ff7b72"  # Red alert for high temperatures
        rect_act = plt.Rectangle((28, i - 0.15), vals_pct[i] * 0.65, 0.3, facecolor=color)
        ax_params.add_patch(rect_act)
        # Render text labels safely without overlap
        ax_params.text(26, i, labels[i], color="#ffffff" if i == active_idx else "#8892b0", fontsize=9, ha="right", va="center", fontweight="bold" if i == active_idx else "normal")

    # ----------------------------------------------------
    # Subplot 2: Global Output Metrics
    # ----------------------------------------------------
    ax_metrics.clear()
    ax_metrics.set_title("GLOBAL PERFORMANCE METRICS", color="#ffffff", fontsize=11, fontweight="bold", pad=12)
    ax_metrics.set_xlim(0, 10)
    ax_metrics.set_ylim(0, 10)
    ax_metrics.axis("off")
    
    # State Banner
    rect_state = plt.Rectangle((0.5, 7.3), 9.0, 2.0, facecolor="#0a192f", edgecolor="#233554", linewidth=1.5)
    ax_metrics.add_patch(rect_state)
    ax_metrics.text(5.0, 8.6, "DEVICE LASING STATE", color="#8892b0", fontsize=8.5, fontweight="bold", ha="center")
    ax_metrics.text(5.0, 7.8, state, color=state_color, fontsize=12, fontweight="bold", ha="center")
    
    # Performance metric values
    ax_metrics.text(1.0, 4.8, "OPTICAL POWER", color="#8892b0", fontsize=9.5, fontweight="bold")
    ax_metrics.text(1.0, 3.6, f"{P_opt_mw:.1f} mW", color="#64ffda", fontsize=18, fontweight="bold")
    
    ax_metrics.text(5.2, 4.8, "WALL-PLUG EFFICIENCY (WPE)", color="#8892b0", fontsize=9.5, fontweight="bold")
    ax_metrics.text(5.2, 3.6, f"{WPE_pct:.2f} %", color="#64ffda", fontsize=18, fontweight="bold")
    
    ax_metrics.text(1.0, 1.8, "TOTAL TERMINAL CURRENT", color="#8892b0", fontsize=9.5, fontweight="bold")
    ax_metrics.text(1.0, 0.8, f"{I_total:.3f} A", color="#ffffff", fontsize=13, fontweight="bold")
    
    # Draw small live trajectory line inside the metric panel
    ax_mini.clear()
    ax_mini.set_facecolor("#0a192f")
    ax_mini.plot(power_history, color="#64ffda", linewidth=1.5)
    ax_mini.set_title("Power Trend (mW)", color="#8892b0", fontsize=7.5)
    ax_mini.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    ax_mini.grid(True, color="#233554", linestyle=":", linewidth=0.5)

    # ----------------------------------------------------
    # Subplot 3: Longitudinal Carrier Profile N(z)
    # ----------------------------------------------------
    ax_carrier.clear()
    ax_carrier.set_title("LONGITUDINAL CARRIER DENSITY N(z) & SHB", color="#ffffff", fontsize=11, fontweight="bold", pad=12)
    ax_carrier.plot(z_grid, N_prof, color="#ff7b72", linewidth=2.5, label="Carrier Density N(z)")
    ax_carrier.set_xlim(0, 100)
    
    # Adaptive y-limit with floor and ceiling guardrails
    ymax_n = max(6.0, max(N_prof) * 1.2)
    ax_carrier.set_ylim(0.0, ymax_n)
    
    ax_carrier.set_xlabel("Cavity Axis Position z (%)", color="#8892b0", fontsize=9.5)
    ax_carrier.set_ylabel("Carrier Density N (10^18 cm^-3)", color="#8892b0", fontsize=9.5)
    ax_carrier.grid(True, color="#233554", linestyle="--", linewidth=0.5)
    ax_carrier.tick_params(colors="#8892b0", labelsize=8.5)
    
    # Label facets
    ax_carrier.axvline(x=0, color="#8892b0", linestyle=":", linewidth=1)
    ax_carrier.axvline(x=100, color="#8892b0", linestyle=":", linewidth=1)
    ax_carrier.text(2, ymax_n * 0.9, "Rear Facet\n(HR, R1)", color="#8892b0", fontsize=7.5, va="top")
    ax_carrier.text(98, ymax_n * 0.9, "Output Facet\n(AR, R2)", color="#8892b0", fontsize=7.5, va="top", ha="right")
    
    # Shaded region / arrow illustrating Spatial Hole Burning near output facet
    if r2 < 0.20 and I_active > 0.08:
        # Carrier dip occurs near z=100
        ax_carrier.annotate("Carrier Dip (SHB)", xy=(90, N_prof[-5]), xytext=(55, N_prof[-5] - 0.8),
                            arrowprops=dict(facecolor='#64ffda', shrink=0.08, width=1.5, headwidth=6),
                            color="#64ffda", fontsize=9, fontweight="bold")
                            
    ax_carrier.legend(loc="lower left", facecolor="#0a192f", edgecolor="#233554", fontsize=8)

    # ----------------------------------------------------
    # Subplot 4: Longitudinal Optical Field Profile P(z)
    # ----------------------------------------------------
    ax_optical.clear()
    ax_optical.set_title("LONGITUDINAL OPTICAL POWER PROFILE P_tot(z)", color="#ffffff", fontsize=11, fontweight="bold", pad=12)
    ax_optical.plot(z_grid, P_prof, color="#64ffda", linewidth=2.5, label="Optical Power P(z)")
    ax_optical.set_xlim(0, 100)
    
    # Adaptive y-limit with floor and ceiling guardrails
    ymax_p = max(100.0, max(P_prof) * 1.2)
    ax_optical.set_ylim(0.0, ymax_p)
    
    ax_optical.set_xlabel("Cavity Axis Position z (%)", color="#8892b0", fontsize=9.5)
    ax_optical.set_ylabel("Optical Power P (mW)", color="#8892b0", fontsize=9.5)
    ax_optical.grid(True, color="#233554", linestyle="--", linewidth=0.5)
    ax_optical.tick_params(colors="#8892b0", labelsize=8.5)
    
    # Label facets
    ax_optical.axvline(x=0, color="#8892b0", linestyle=":", linewidth=1)
    ax_optical.axvline(x=100, color="#8892b0", linestyle=":", linewidth=1)
    ax_optical.text(2, ymax_p * 0.9, "HR Facet\n(R1)", color="#8892b0", fontsize=7.5, va="top")
    ax_optical.text(98, ymax_p * 0.9, "AR Facet\n(R2)", color="#8892b0", fontsize=7.5, va="top", ha="right")
    
    ax_optical.legend(loc="upper left", facecolor="#0a192f", edgecolor="#233554", fontsize=8)

    # Figure headers and descriptions
    fig.suptitle(phase_title, color="#64ffda", fontsize=17, fontweight="bold", y=0.96)
    fig.text(0.5, 0.91, phase_desc, color="#ffffff", fontsize=10.5, ha="center")
    fig.text(0.94, 0.96, f"Frame {frame+1}/{total_frames}", color="#8892b0", fontsize=9, ha="right")
    fig.text(0.06, 0.96, "PLaser SURROGATE MODEL DASHBOARD", color="#ffffff", fontsize=11, fontweight="bold")

    write_frame_to_video()
    
    # Print progress
    if (frame + 1) % 60 == 0:
        print(f"Rendered {frame+1}/{total_frames} frames...")

# Cleanup
video.release()
plt.close(fig)
print(f"Animation successfully saved to {video_path}")
