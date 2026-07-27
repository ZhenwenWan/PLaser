#!/usr/bin/env python3
"""
Generate a high-fidelity MP4 demonstration video for PLaser.
Sweeps design parameters in real-time and visualizes multiphysics steady states.
Uses Matplotlib for rendering a dark-themed dashboard and OpenCV for compiling the MP4.
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import cv2

# Set backend to Agg for headless canvas rendering
import matplotlib
matplotlib.use('Agg')

import sys
sys.path.insert(0, r"C:\Users\aw4wz\Documents\Codex\Lasers\Lasers\Libs")

# Import PLaser surrogate wrapper
from pinn_surrogate import PINNSurrogate

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
    raise RuntimeError("Failed to open OpenCV VideoWriter.")

print(f"Generating animation ({total_frames} frames)...")

# Define Sweep Profiles
# Frame 0-120: Reflectivity sweep
# Frame 120-240: Current sweep
# Frame 240-360: Temperature sweep
r1_seq = np.ones(total_frames) * 0.9
r2_seq = np.ones(total_frames) * 0.3
L_seq = np.ones(total_frames) * 300.0
T0_seq = np.ones(total_frames) * 300.0
I_seq = np.ones(total_frames) * 0.18

# 1. Reflectivity R2 sweep: 0.05 -> 0.9 -> 0.05
r2_seq[0:60] = np.linspace(0.05, 0.90, 60)
r2_seq[60:120] = np.linspace(0.90, 0.05, 60)

# 2. Current sweep: 0.01A -> 0.35A -> 0.01A
I_seq[120:180] = np.linspace(0.01, 0.35, 60)
I_seq[180:240] = np.linspace(0.35, 0.01, 60)
# Fix R2 for the rest of sweeps to 0.05 to show strong asymmetric SHB
r2_seq[120:] = 0.05

# 3. Temperature sweep: 250K -> 360K -> 250K
T0_seq[240:300] = np.linspace(250.0, 360.0, 60)
T0_seq[300:360] = np.linspace(360.0, 250.0, 60)

# Setup Matplotlib Figure
plt.style.use('dark_background')
fig = plt.figure(figsize=(16, 9), facecolor="#0a192f")
# GridSpec for clean layout
gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.25, left=0.06, right=0.94, top=0.88, bottom=0.08)

# Create 4 Subplots
ax_params = fig.add_subplot(gs[0, 0], facecolor="#172a45")
ax_metrics = fig.add_subplot(gs[0, 1], facecolor="#172a45")
ax_carrier = fig.add_subplot(gs[1, 0], facecolor="#172a45")
ax_optical = fig.add_subplot(gs[1, 1], facecolor="#172a45")
ax_mini = fig.add_axes([0.76, 0.58, 0.16, 0.10], facecolor="#0a192f")

z_grid = np.linspace(0, 100, 51)  # Normalised z grid (%)

# History list for plotting scalar trajectories
power_history = []
wpe_history = []

for frame in range(total_frames):
    # Current sweep values
    r1 = r1_seq[frame]
    r2 = r2_seq[frame]
    L = L_seq[frame]
    T0 = T0_seq[frame]
    I_active = I_seq[frame]
    
    # Run PINN prediction (5 ms latency)
    res = surrogate.predict(R1=r1, R2=r2, L_um=L, T0=T0, I_active=I_active)
    
    P_opt_mw = res["P_opt"] * 1000.0  # Convert to mW
    WPE_pct = res["wpe"] * 100.0       # Convert to %
    I_total = res["I_total"]
    N_prof = res["N"] / 1.0e18         # Normalize to 1e18 cm^-3
    P_prof = res["P"] * 1000.0     # Convert profile to mW
    
    power_history.append(P_opt_mw)
    wpe_history.append(WPE_pct)
    
    # Limit histories to keep plot clean
    if len(power_history) > 60:
        power_history.pop(0)
        wpe_history.pop(0)
        
    # Determine operation state
    if I_active < 0.05:
        state = "BELOW THRESHOLD"
        state_color = "#8892b0"
    elif T0 > 340.0 and P_opt_mw < 10.0:
        state = "THERMAL DROOP"
        state_color = "#ff7b72"
    else:
        state = "ACTIVE LASING"
        state_color = "#64ffda"

    # ----------------------------------------------------
    # Subplot 1: Live Parameter Swings (Progress Bars)
    # ----------------------------------------------------
    ax_params.clear()
    ax_params.set_title("DESIGN OPTION CONTROLS (LIVE SWEEP)", color="#ffffff", fontsize=11, fontweight="bold", pad=12)
    ax_params.set_xlim(0, 100)
    ax_params.set_ylim(-0.5, 4.5)
    ax_params.axis("off")
    
    # Render progress bars
    labels = [
        f"Mirror 1 Reflectivity (R1): {r1:.2f}",
        f"Mirror 2 Reflectivity (R2): {r2:.2f}",
        f"Cavity Length (L): {L:.0f} um",
        f"Operating Temp (T0): {T0:.1f} K",
        f"Active Current (I_act): {I_active:.3f} A"
    ]
    # Current values scaled to 0-100% for progress bars
    vals_pct = [
        r1 * 100.0,
        r2 * 100.0,
        (L - 100.0) / 900.0 * 100.0,
        (T0 - 250.0) / 110.0 * 100.0,
        (I_active - 0.01) / 0.49 * 100.0
    ]
    
    for i in range(5):
        # Draw background bar
        rect_bg = plt.Rectangle((15, i - 0.15), 80, 0.3, facecolor="#0a192f", edgecolor="#233554")
        ax_params.add_patch(rect_bg)
        # Draw active bar
        rect_act = plt.Rectangle((15, i - 0.15), vals_pct[i] * 0.8, 0.3, facecolor="#64ffda" if i != 3 else "#ff7b72")
        ax_params.add_patch(rect_act)
        # Render text labels
        ax_params.text(14, i, labels[i], color="#ffffff", fontsize=9.5, ha="right", va="center")

    # ----------------------------------------------------
    # Subplot 2: Global Output Metrics & Lasing State
    # ----------------------------------------------------
    ax_metrics.clear()
    ax_metrics.set_title("GLOBAL OPTICAL PERFORMANCE METRICS", color="#ffffff", fontsize=11, fontweight="bold", pad=12)
    ax_metrics.set_xlim(0, 10)
    ax_metrics.set_ylim(0, 10)
    ax_metrics.axis("off")
    
    # State Banner
    rect_state = plt.Rectangle((0.5, 7.5), 9.0, 1.8, facecolor="#0a192f", edgecolor="#233554", linewidth=1.5)
    ax_metrics.add_patch(rect_state)
    ax_metrics.text(5.0, 8.7, "DEVICE LASING STATE", color="#8892b0", fontsize=8.5, fontweight="bold", ha="center")
    ax_metrics.text(5.0, 8.0, state, color=state_color, fontsize=15, fontweight="bold", ha="center")
    
    # Performance metric values
    ax_metrics.text(1.0, 5.0, "OPTICAL POWER", color="#8892b0", fontsize=9.5, fontweight="bold")
    ax_metrics.text(1.0, 3.8, f"{P_opt_mw:.1f} mW", color="#64ffda", fontsize=18, fontweight="bold")
    
    ax_metrics.text(5.5, 5.0, "WALL-PLUG EFFICIENCY (WPE)", color="#8892b0", fontsize=9.5, fontweight="bold")
    ax_metrics.text(5.5, 3.8, f"{WPE_pct:.2f} %", color="#64ffda", fontsize=18, fontweight="bold")
    
    ax_metrics.text(1.0, 2.0, "TOTAL CURRENT", color="#8892b0", fontsize=9.5, fontweight="bold")
    ax_metrics.text(1.0, 1.0, f"{I_total:.3f} A", color="#ffffff", fontsize=14, fontweight="bold")
    
    # Draw small live trajectory line inside the metric panel
    ax_mini.clear()
    # Explicitly set facecolor again after clear
    ax_mini.set_facecolor("#0a192f")
    ax_mini.plot(power_history, color="#64ffda", linewidth=1.5)
    ax_mini.set_title("Power Trend (mW)", color="#8892b0", fontsize=7.5)
    ax_mini.tick_params(left=False, labelleft=False, bottom=False, labelbottom=False)
    ax_mini.grid(True, color="#233554", linestyle=":", linewidth=0.5)

    # ----------------------------------------------------
    # Subplot 3: Longitudinal Carrier Profile N(z)
    # ----------------------------------------------------
    ax_carrier.clear()
    ax_carrier.set_title("LONGITUDINAL CARRIER DENSITY N(z) (SPATIAL HOLE BURNING)", color="#ffffff", fontsize=11, fontweight="bold", pad=12)
    ax_carrier.plot(z_grid, N_prof, color="#ff7b72", linewidth=2.5, label="Carrier Density N(z)")
    ax_carrier.set_xlim(0, 100)
    ax_carrier.set_ylim(0.0, 6.0)
    ax_carrier.set_xlabel("Cavity Axis Position z (%)", color="#8892b0", fontsize=9.5)
    ax_carrier.set_ylabel("Density N (10^18 cm^-3)", color="#8892b0", fontsize=9.5)
    ax_carrier.grid(True, color="#233554", linestyle="--", linewidth=0.5)
    ax_carrier.tick_params(colors="#8892b0", labelsize=8.5)
    
    # Add labels showing threshold clamping
    ax_carrier.axhline(y=1.0, color="#8892b0", linestyle=":", label="Transparency Threshold N_tr")
    ax_carrier.legend(loc="upper right", facecolor="#0a192f", edgecolor="#233554", fontsize=8)

    # ----------------------------------------------------
    # Subplot 4: Longitudinal Optical Field Profile P(z)
    # ----------------------------------------------------
    ax_optical.clear()
    ax_optical.set_title("LONGITUDINAL OPTICAL POWER PROFILE P_tot(z)", color="#ffffff", fontsize=11, fontweight="bold", pad=12)
    ax_optical.plot(z_grid, P_prof, color="#64ffda", linewidth=2.5, label="Optical Power P(z)")
    ax_optical.set_xlim(0, 100)
    ax_optical.set_ylim(0.0, 450.0)
    ax_optical.set_xlabel("Cavity Axis Position z (%)", color="#8892b0", fontsize=9.5)
    ax_optical.set_ylabel("Optical Power P (mW)", color="#8892b0", fontsize=9.5)
    ax_optical.grid(True, color="#233554", linestyle="--", linewidth=0.5)
    ax_optical.tick_params(colors="#8892b0", labelsize=8.5)
    ax_optical.legend(loc="upper left", facecolor="#0a192f", edgecolor="#233554", fontsize=8)

    # Add page title/header
    fig.suptitle("PLaser MULTI-PHYSICS SIMULATION DASHBOARD", color="#ffffff", fontsize=18, fontweight="bold", y=0.96)
    fig.text(0.5, 0.91, f"Frame {frame+1}/{total_frames}  |  Real-Time PINN Inference Latency: < 5 ms", color="#8892b0", fontsize=11, ha="center")

    # Render frame to canvas
    fig.canvas.draw()
    
    # Convert RGBA buffer to BGR numpy array for OpenCV
    img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    # Resize to exact width/height just in case DPI settings skew it
    img_bgr = cv2.resize(img_bgr, (width, height))
    
    # Write to MP4 file
    video.write(img_bgr)
    
    # Print progress every 60 frames
    if (frame + 1) % 60 == 0:
        print(f"Rendered {frame+1}/{total_frames} frames...")

# Cleanup
video.release()
plt.close(fig)
print(f"Animation successfully saved to {video_path}")
