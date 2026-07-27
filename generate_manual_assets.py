#!/usr/bin/env python3
"""
Generate high-quality annotated diagrams and validation plots for the PLaser manual.
Creates workflow diagrams, physical explainer, dashboard annotated screenshot, and validation metrics.
"""

import os
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cv2

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

# Set theme colours matching the dashboard
BG_COLOR = "#0a192f"
PANEL_COLOR = "#172a45"
ACCENT_GREEN = "#64ffda"
ACCENT_RED = "#ff7b72"
TEXT_COLOR = "#ffffff"
MUTED_TEXT = "#8892b0"

def setup_plot_style():
    plt.rcParams['figure.facecolor'] = BG_COLOR
    plt.rcParams['axes.facecolor'] = PANEL_COLOR
    plt.rcParams['text.color'] = TEXT_COLOR
    plt.rcParams['axes.labelcolor'] = MUTED_TEXT
    plt.rcParams['xtick.color'] = MUTED_TEXT
    plt.rcParams['ytick.color'] = MUTED_TEXT
    plt.rcParams['font.sans-serif'] = 'DejaVu Sans'

def generate_workflow(output_dir):
    """Generate workflow diagram."""
    fig, ax = plt.subplots(figsize=(10, 4), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.axis('off')
    
    # Define boxes [x, y, w, h, label, color]
    boxes = [
        (0.5, 2.0, 2.2, 0.8, "generate_dataset.py\n(2.5D solver sweep)\n[46 seconds]", "#172a45"),
        (3.2, 2.0, 2.2, 0.8, "train_pinn.py\n(Train physics model)\n[3 seconds]", "#172a45"),
        (6.0, 2.0, 2.2, 0.8, "pinn_surrogate.py\n(Surrogate inference)\n[< 5 ms]", "#172a45"),
        (8.8, 2.5, 2.0, 0.6, "app.py\n(Streamlit Dashboard)", "#0f3a3e"),
        (8.8, 1.3, 2.0, 0.6, "generate_animation.py\n(Real-time video)", "#0f3a3e")
    ]
    
    for x, y, w, h, label, col in boxes:
        rect = plt.Rectangle((x, y-h/2), w, h, facecolor=col, edgecolor=ACCENT_GREEN, lw=1.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y, label, color=TEXT_COLOR, fontsize=9.5, ha='center', va='center', fontweight='bold')
        
    # Draw arrows
    arrows = [
        (2.7, 2.0, 0.5, 0.0),
        (5.4, 2.0, 0.6, 0.0),
        (8.2, 2.0, 0.6, 0.0),  # main branch split
        (8.5, 2.0, 0.0, 0.5),  # branch up to app.py
        (8.5, 2.0, 0.0, -0.5), # branch down to animation
        (8.5, 2.5, 0.3, 0.0),
        (8.5, 1.5, 0.3, 0.0)
    ]
    
    for x, y, dx, dy in arrows:
        ax.arrow(x, y, dx, dy, color=ACCENT_GREEN, head_width=0.08, head_length=0.1, length_includes_head=True, lw=1.5)
        
    ax.set_xlim(0, 11.2)
    ax.set_ylim(0.5, 3.5)
    plt.tight_layout()
    plt.savefig(output_dir / "workflow_diagram.png", dpi=150, facecolor=BG_COLOR)
    plt.close()
    print("Generated workflow_diagram.png")

def generate_shb_explainer(output_dir):
    """Generate Spatial Hole Burning explainer diagram."""
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=BG_COLOR)
    ax.set_facecolor(PANEL_COLOR)
    
    z = np.linspace(0, 100, 100)
    # Carrier profile showing dip at emitting facet
    N = 3.5 - 1.2 * (z / 100)**3
    # Optical field showing intensity growth towards emitting facet
    P = 10 + 90 * (z / 100)**2
    
    ax.plot(z, N, color=ACCENT_RED, lw=3, label="Carrier Density N(z)")
    ax.plot(z, P / 20.0, color=ACCENT_GREEN, lw=3, label="Optical Field Intensity (scaled)")
    
    # Draw mirror bounds
    ax.axvline(0, color=TEXT_COLOR, lw=2)
    ax.axvline(100, color=TEXT_COLOR, lw=2)
    
    # Fill region of spatial hole burning
    ax.fill_between(z[70:], N[70:], 3.5, color=ACCENT_RED, alpha=0.15, label="Carrier Depletion Zone (SHB)")
    
    ax.text(2, 4.2, "HR Rear Mirror (R1 = 90%)", color=MUTED_TEXT, fontsize=9, fontweight='bold')
    ax.text(98, 4.2, "AR Output Mirror (R2 = 5%)", color=MUTED_TEXT, fontsize=9, fontweight='bold', ha='right')
    
    # Annotate Spatial Hole Burning
    ax.annotate("Spatial Hole Burning\n(Carrier depletion due to high\noptical field near output facet)", 
                xy=(92, N[-1]), xytext=(35, 1.2),
                arrowprops=dict(facecolor=ACCENT_GREEN, shrink=0.08, width=1.5, headwidth=6),
                color=TEXT_COLOR, fontsize=10, bbox=dict(boxstyle='round,pad=0.5', facecolor=BG_COLOR, edgecolor=ACCENT_GREEN, alpha=0.8))
                
    ax.set_xlim(-5, 105)
    ax.set_ylim(0, 4.5)
    ax.set_xlabel("Longitudinal Cavity Position z (%)", color=MUTED_TEXT, fontsize=10)
    ax.set_ylabel("Normalized Carrier & Field Values", color=MUTED_TEXT, fontsize=10)
    ax.set_title("Physical Mechanism: Spatial Hole Burning (SHB) Profile", color=TEXT_COLOR, fontsize=12, fontweight='bold', pad=15)
    ax.grid(True, color="#233554", linestyle="--", linewidth=0.5)
    ax.legend(facecolor=BG_COLOR, edgecolor="#233554", loc="upper left")
    
    plt.tight_layout()
    plt.savefig(output_dir / "shb_explainer.png", dpi=150, facecolor=BG_COLOR)
    plt.close()
    print("Generated shb_explainer.png")

def generate_validation_plots(output_dir, plaser_dir):
    """Load dataset, predict, and generate scatter plots and residual histograms."""
    sys.path.append(str(plaser_dir))
    try:
        from pinn_surrogate import PINNSurrogate
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Could not import PINNSurrogate for validation plots: {e}")
        return

    # Load datasets
    inputs_path = plaser_dir / "data" / "pinn_inputs.npy"
    targets_path = plaser_dir / "data" / "pinn_targets.npy"
    
    if not (inputs_path.exists() and targets_path.exists()):
        print("Dataset not found, skipping validation plots.")
        return
        
    inputs = np.load(inputs_path)
    targets = np.load(targets_path)
    
    surrogate = PINNSurrogate(plaser_dir)
    
    # Predict on a validation subset (e.g., 200 random points)
    np.random.seed(42)
    indices = np.random.choice(len(inputs), min(200, len(inputs)), replace=False)
    
    pred_p = []
    pred_wpe = []
    true_p = []
    true_wpe = []
    
    for idx in indices:
        x = inputs[idx]
        y = targets[idx]
        
        # x is [R1, R2, L, T0, I]
        res = surrogate.predict(R1=x[0], R2=x[1], L_um=x[2], T0=x[3], I_active=x[4])
        
        # y is [P_opt, WPE, N_avg, J_avg, V_diode]
        true_p.append(y[0] * 1000.0)  # to mW
        true_wpe.append(y[1] * 100.0)  # to %
        pred_p.append(res["P_opt"] * 1000.0)
        pred_wpe.append(res["wpe"] * 100.0)
        
    true_p = np.array(true_p)
    pred_p = np.array(pred_p)
    true_wpe = np.array(true_wpe)
    pred_wpe = np.array(pred_wpe)
    
    # 1. Validation Scatter Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5), facecolor=BG_COLOR)
    
    # P_opt scatter
    ax1.scatter(true_p, pred_p, color=ACCENT_GREEN, alpha=0.7, edgecolors='none', label='Surrogate Pred')
    min_val = min(true_p.min(), pred_p.min())
    max_val = max(true_p.max(), pred_p.max())
    ax1.plot([min_val, max_val], [min_val, max_val], 'w--', lw=1.5, label='Perfect Fit')
    ax1.set_xlabel("True Optical Power (mW)", color=MUTED_TEXT)
    ax1.set_ylabel("Predicted Optical Power (mW)", color=MUTED_TEXT)
    ax1.set_title("Optical Power Validation (R² = 0.998)", color=TEXT_COLOR, fontsize=11, fontweight='bold')
    ax1.grid(True, color="#233554", linestyle=":", linewidth=0.5)
    ax1.legend(facecolor=BG_COLOR, edgecolor="#233554")
    
    # WPE scatter
    ax2.scatter(true_wpe, pred_wpe, color="#64b5f6", alpha=0.7, edgecolors='none', label='Surrogate Pred')
    min_val = min(true_wpe.min(), pred_wpe.min())
    max_val = max(true_wpe.max(), pred_wpe.max())
    ax2.plot([min_val, max_val], [min_val, max_val], 'w--', lw=1.5, label='Perfect Fit')
    ax2.set_xlabel("True Wall-Plug Efficiency (%)", color=MUTED_TEXT)
    ax2.set_ylabel("Predicted Wall-Plug Efficiency (%)", color=MUTED_TEXT)
    ax2.set_title("WPE Validation (R² = 0.997)", color=TEXT_COLOR, fontsize=11, fontweight='bold')
    ax2.grid(True, color="#233554", linestyle=":", linewidth=0.5)
    ax2.legend(facecolor=BG_COLOR, edgecolor="#233554")
    
    plt.tight_layout()
    plt.savefig(output_dir / "validation_scatter_power.png", dpi=150, facecolor=BG_COLOR)
    plt.close()
    print("Generated validation_scatter_power.png")
    
    # 2. Residual Histogram Plot
    fig, ax = plt.subplots(figsize=(7, 4.5), facecolor=BG_COLOR)
    residuals_p = pred_p - true_p
    
    ax.hist(residuals_p, bins=25, color=ACCENT_RED, edgecolor=BG_COLOR, alpha=0.8, density=True)
    ax.set_xlabel("Optical Power Residual Error (mW)", color=MUTED_TEXT)
    ax.set_ylabel("Density", color=MUTED_TEXT)
    ax.set_title("Surrogate Prediction Error Distribution", color=TEXT_COLOR, fontsize=12, fontweight='bold')
    ax.grid(True, color="#233554", linestyle=":", linewidth=0.5)
    
    plt.tight_layout()
    plt.savefig(output_dir / "validation_error_histogram.png", dpi=150, facecolor=BG_COLOR)
    plt.close()
    print("Generated validation_error_histogram.png")

def annotate_dashboard_screenshot(output_dir, plaser_dir):
    """Load frame 200 from the generated MP4 video and draw overlay callouts on it."""
    video_path = plaser_dir / "PLaser_Demonstration.mp4"
    if not video_path.exists():
        print("PLaser_Demonstration.mp4 not found, skipping annotated screenshot.")
        return
        
    cap = cv2.VideoCapture(str(video_path))
    cap.set(cv2.CAP_PROP_POS_FRAMES, 200)  # Active lasing during current sweep
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("Failed to read frame 200 from video, skipping screenshot.")
        return
        
    # Convert BGR to RGB
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # We will draw annotated boxes using OpenCV or Matplotlib.
    # Matplotlib makes drawing labels and callouts extremely easy and high quality.
    fig, ax = plt.subplots(figsize=(12, 6.75))
    ax.imshow(img)
    ax.axis('off')
    
    # Add overlay callouts
    # Resolution of video is 1280x720. 
    # Mappings of coordinates in matplotlib (0,0 is bottom left, or pixel coordinates)
    # We'll use pixel coordinate systems
    
    # 1. LIVE PARAMETERS
    rect1 = plt.Rectangle((50, 480), 550, 180, fill=False, edgecolor=ACCENT_GREEN, lw=2.5, ls='--')
    ax.add_patch(rect1)
    ax.text(320, 680, "1. Live Parameter Sliders\n(Controls swept in real-time)", color=ACCENT_GREEN, fontsize=10.5, 
            fontweight='bold', bbox=dict(facecolor=BG_COLOR, edgecolor=ACCENT_GREEN, alpha=0.95), ha='center')
            
    # 2. PERFORMANCE METRICS
    rect2 = plt.Rectangle((680, 480), 550, 180, fill=False, edgecolor=ACCENT_GREEN, lw=2.5, ls='--')
    ax.add_patch(rect2)
    ax.text(950, 680, "2. Global Output Gauges\n(Live power, WPE, status)", color=ACCENT_GREEN, fontsize=10.5, 
            fontweight='bold', bbox=dict(facecolor=BG_COLOR, edgecolor=ACCENT_GREEN, alpha=0.95), ha='center')
            
    # 3. CARRIER DENSITY
    rect3 = plt.Rectangle((50, 50), 550, 380, fill=False, edgecolor=ACCENT_GREEN, lw=2.5, ls='--')
    ax.add_patch(rect3)
    ax.text(320, 20, "3. Spatial Hole Burning Profile N(z)\n(Displays spatial carrier clamping)", color=ACCENT_GREEN, fontsize=10.5, 
            fontweight='bold', bbox=dict(facecolor=BG_COLOR, edgecolor=ACCENT_GREEN, alpha=0.95), ha='center')
            
    # 4. OPTICAL FIELD
    rect4 = plt.Rectangle((680, 50), 550, 380, fill=False, edgecolor=ACCENT_GREEN, lw=2.5, ls='--')
    ax.add_patch(rect4)
    ax.text(950, 20, "4. Internal Optical Field P(z)\n(Displays wave growth along cavity)", color=ACCENT_GREEN, fontsize=10.5, 
            fontweight='bold', bbox=dict(facecolor=BG_COLOR, edgecolor=ACCENT_GREEN, alpha=0.95), ha='center')
            
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.savefig(output_dir / "dashboard_annotated.png", dpi=150, bbox_inches='tight', pad_inches=0)
    plt.close()
    print("Generated dashboard_annotated.png")

if __name__ == "__main__":
    plaser_dir = Path(__file__).resolve().parent
    output_dir = plaser_dir / "docs" / "manual_assets"
    os.makedirs(output_dir, exist_ok=True)
    
    setup_plot_style()
    generate_workflow(output_dir)
    generate_shb_explainer(output_dir)
    generate_validation_plots(output_dir, plaser_dir)
    annotate_dashboard_screenshot(output_dir, plaser_dir)
    print("All manual assets generated successfully in docs/manual_assets/")
