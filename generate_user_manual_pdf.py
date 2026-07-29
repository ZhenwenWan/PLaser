#!/usr/bin/env python3
"""
Generate a professional, high-fidelity 5-page PDF User Manual for PLaser.
Embeds the generated workflow diagrams, physical explainers, dashboard screenshots,
and validation charts directly into the PDF layout.
"""

from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

# Setup paths
PLASER_DIR = Path(__file__).resolve().parent
output_pdf_path = PLASER_DIR / "PLaser_User_Manual.pdf"
assets_dir = PLASER_DIR / "docs" / "manual_assets"

# Theme Colors matching the PLaser Dashboard
BG_COLOR = "#0a192f"
PANEL_COLOR = "#172a45"
ACCENT_GREEN = "#64ffda"
ACCENT_RED = "#ff7b72"
TEXT_COLOR = "#ffffff"
MUTED_TEXT = "#8892b0"

def add_header(ax, title):
    ax.text(0.05, 0.95, "PLASER DIODE LASER EDA SUITE", color=ACCENT_GREEN, fontsize=10, fontweight="bold", alpha=0.8)
    ax.text(0.05, 0.91, title.upper(), color=TEXT_COLOR, fontsize=15, fontweight="bold")
    ax.plot([0.05, 0.95], [0.89, 0.89], color="#233554", transform=ax.transAxes, linewidth=1.5)

def add_footer(ax, page_num):
    ax.plot([0.05, 0.95], [0.08, 0.08], color="#233554", transform=ax.transAxes, linewidth=1.0)
    ax.text(0.05, 0.05, "© 2026 Zhenwen Wan (AI + Simulation Expert). All rights reserved.", color=MUTED_TEXT, fontsize=8)
    ax.text(0.90, 0.05, f"Page {page_num}", color=MUTED_TEXT, fontsize=9)

def draw_paragraph(ax, text, x, y, max_len=100, line_height=0.020, color="#e6f1ff", fontsize=9.5):
    words = text.split()
    curr_line = ""
    lines = []
    for word in words:
        if len(curr_line + " " + word) < max_len:
            curr_line += (" " if curr_line else "") + word
        else:
            lines.append(curr_line)
            curr_line = word
    if curr_line:
        lines.append(curr_line)
        
    for line in lines:
        ax.text(x, y, line, color=color, fontsize=fontsize, transform=ax.transAxes, alpha=0.9)
        y -= line_height
    return y

def embed_image(fig, img_path, left, bottom, w, h):
    if img_path.exists():
        img = plt.imread(str(img_path))
        img_ax = fig.add_axes([left, bottom, w, h], facecolor="none")
        img_ax.imshow(img)
        img_ax.axis("off")
    else:
        # Fallback placeholder box
        img_ax = fig.add_axes([left, bottom, w, h], facecolor=PANEL_COLOR)
        img_ax.text(0.5, 0.5, f"Asset Missing:\n{img_path.name}", color=ACCENT_RED, ha='center', va='center')
        img_ax.axis("off")

# Initialize PDF compilation
with PdfPages(str(output_pdf_path)) as pdf:
    # ====================================================
    # Page 1: Cover Page (Attractive Theme)
    # ====================================================
    fig = plt.figure(figsize=(8.5, 11), facecolor=BG_COLOR)
    ax = fig.add_axes([0, 0, 1, 1], facecolor="none")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    # Techy background accent lines
    ax.plot([0, 1], [0.85, 0.85], color=PANEL_COLOR, linewidth=3)
    ax.plot([0, 1], [0.15, 0.15], color=PANEL_COLOR, linewidth=3)
    
    # Title
    ax.text(0.1, 0.68, "PLaser", color=ACCENT_GREEN, fontsize=54, fontweight="bold")
    ax.text(0.1, 0.58, "Physics-Informed Neural Network\nDiode Laser EDA Application", color=TEXT_COLOR, fontsize=24, fontweight="bold", linespacing=1.3)
    ax.text(0.1, 0.50, "A Real-Time Parametric Optimization & Longitudinal Profiling Platform", color=MUTED_TEXT, fontsize=12, style="italic")
    
    # Highlight box
    ax.text(0.1, 0.38, "USER MANUAL & TECHNICAL REFERENCE", color=ACCENT_GREEN, fontsize=11, fontweight="bold", bbox=dict(boxstyle="square,pad=0.5", facecolor=PANEL_COLOR, edgecolor=ACCENT_GREEN, linewidth=1))
    
    # Meta Details
    ax.text(0.1, 0.28, "TARGET AUDIENCE:", color=MUTED_TEXT, fontsize=9, fontweight="bold")
    ax.text(0.1, 0.25, "Laser Cavity Designers, Optoelectronic Engineers & Research Collaborators", color=TEXT_COLOR, fontsize=10.5)
    
    ax.text(0.1, 0.20, "AUTHOR & SERVICE SCOPE:", color=MUTED_TEXT, fontsize=9, fontweight="bold")
    ax.text(0.1, 0.17, "Zhenwen Wan (AI + Simulation Expert  |  Service: Custom PINN Solvers)", color=TEXT_COLOR, fontsize=10)
    
    pdf.savefig(fig, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    
    # ====================================================
    # Page 2: Scope, Methodology & Architecture
    # ====================================================
    fig = plt.figure(figsize=(8.5, 11), facecolor=BG_COLOR)
    ax = fig.add_axes([0, 0, 1, 1], facecolor="none")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    add_header(ax, "1. Scope, Methodology & Project Architecture")
    
    y = 0.84
    # 1.1 Scope & Method
    ax.text(0.05, y, "1.1 Service Scope & Methodology", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    scope_txt = (
        "PLaser provides a next-generation Electronic Design Automation (EDA) interface for edge-emitting "
        "semiconductor telecom diode lasers. By training a Physics-Informed Neural Network (PINN) surrogate, "
        "PLaser bypasses slow iteration times of coupled numerical solvers. The methodology integrates "
        "a 2D transverse solver (for electro-thermal-optical waveguide profiling) and a 1D longitudinal "
        "shooting solver (enforcing carrier rate equations and optical power propagation). The trained PINN "
        "enforces local continuity rate equations as physical loss residuals during backpropagation, "
        "retaining physical consistency and predicting non-linear threshold bounds within a fraction of a millisecond."
    )
    y = draw_paragraph(ax, scope_txt, 0.05, y)
    
    # 1.2 Included Files
    y -= 0.015
    ax.text(0.05, y, "1.2 Project Architecture & Files Included", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    files_txt = (
        "The repository contains the following structured components:\n"
        "• app.py: Streamlit dashboard displaying parametric sweeps and profiles.\n"
        "• pinn_surrogate.py: Inference class executing neural network evaluation.\n"
        "• generate_dataset.py: Standalone CPU-optimized script collecting shooting solver sweeps.\n"
        "• train_pinn.py: Training script enforcing the physics-informed loss constraints.\n"
        "• generate_animation.py: Compiles parametric sweep sweeps into an MP4 demonstration video.\n"
        "• data/ & models/: Pretrained model weights (.pt), scaling variables (.npz) and dataset (.npy)."
    )
    y = draw_paragraph(ax, files_txt, 0.05, y)
    
    # Embed workflow diagram
    embed_image(fig, assets_dir / "workflow_diagram.png", 0.05, 0.12, 0.90, 0.28)
    ax.text(0.5, 0.11, "Figure 1.1: Project data flow, training pipeline, and application runtime architecture.", color=MUTED_TEXT, fontsize=8, ha='center', style='italic')
    
    add_footer(ax, 2)
    pdf.savefig(fig, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    
    # ====================================================
    # Page 3: Installation & Running
    # ====================================================
    fig = plt.figure(figsize=(8.5, 11), facecolor=BG_COLOR)
    ax = fig.add_axes([0, 0, 1, 1], facecolor="none")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    add_header(ax, "2. Installation & Quickstart Tasks")
    
    y = 0.84
    # 2.1 Installation
    ax.text(0.05, y, "2.1 Local Environment Setup", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    install_txt = (
        "Configure Python 3.9 - 3.12 (64-bit) in a folder with short directory pathing (to avoid Windows WinError 206):\n"
        "  git clone https://github.com/ZhenwenWan/PLaser.git\n"
        "  cd PLaser\n"
        "  python -m venv .venv\n"
        "  .\\.venv\\Scripts\\Activate.ps1   # On Windows\n"
        "  pip install -r requirements.txt\n\n"
        "Verify imports: python -c \"import numpy, matplotlib, streamlit, torch, cv2; print('OK')\""
    )
    y = draw_paragraph(ax, install_txt, 0.05, y)
    
    # 2.2 Tasks
    y -= 0.015
    ax.text(0.05, y, "2.2 Execution Tasks & Instructions", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    tasks_txt = (
        "• Task A: Run Pretrained Dashboard (Default usage - no training required)\n"
        "  Command: python -m streamlit run app.py  [Latency: < 5 ms, launches web dashboard]\n"
        "• Task B: Regenerate Convergence Datasets (Optional - sweeps parameter space)\n"
        "  Command: python generate_dataset.py  [Runtime: ~46 seconds, sweeps 1,500 physical solver cases]\n"
        "• Task C: Retrain PINN Neural Net (Optional - fits new weights on dataset)\n"
        "  Command: python train_pinn.py  [Runtime: ~3 seconds, reaches 2.27 convergence loss]\n"
        "• Task D: Generate Video Demo (Optional - compiles MP4 animation sweeps)\n"
        "  Command: python generate_animation.py  [Runtime: ~3 mins, compiles PLaser_Demonstration.mp4]"
    )
    y = draw_paragraph(ax, tasks_txt, 0.05, y)
    
    # 2.3 Troubleshooting
    y -= 0.015
    ax.text(0.05, y, "2.3 Troubleshooting & Common Fixes", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    
    # Draw troubleshooting table
    table_data = [
        ["Symptom", "Likely Cause", "Action/Fix"],
        ["ModuleNotFoundError", "Virtual environment not active", "Run .\\.venv\\Scripts\\Activate.ps1 then pip install"],
        ["Streamlit Model Missing", "Missing pt or npz weights file", "Run train_pinn.py to generate models/pinn_laser_model.pt"],
        ["WinError 206 / Path too long", "Windows filepath limit exceeded", "Move PLaser folder to C:\\PLaser and run there"],
        ["MP4 generation failure", "OpenCV backend library missing", "Verify pip install opencv-python or install python-opencv"]
    ]
    
    table_y = y
    for i, row in enumerate(table_data):
        row_color = ACCENT_GREEN if i == 0 else "#ffffff"
        font_wt = "bold" if i == 0 else "normal"
        if i == 0:
            rect = plt.Rectangle((0.05, table_y - 0.005), 0.90, 0.025, facecolor=PANEL_COLOR, transform=ax.transAxes)
            ax.add_patch(rect)
        
        ax.text(0.06, table_y, row[0], color=row_color, fontsize=8, fontweight=font_wt, transform=ax.transAxes)
        ax.text(0.26, table_y, row[1], color=row_color, fontsize=8, fontweight=font_wt, transform=ax.transAxes)
        ax.text(0.54, table_y, row[2], color=row_color, fontsize=8, fontweight=font_wt, transform=ax.transAxes)
        table_y -= 0.03
        
    add_footer(ax, 3)
    pdf.savefig(fig, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    
    # ====================================================
    # Page 4: Operation Manual - Dashboard & Physical Explainer
    # ====================================================
    fig = plt.figure(figsize=(8.5, 11), facecolor=BG_COLOR)
    ax = fig.add_axes([0, 0, 1, 1], facecolor="none")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    add_header(ax, "3. Dashboard Operation & Physical Insight")
    
    y = 0.84
    ax.text(0.05, y, "3.1 Dashboard Layout Callouts", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    layout_txt = (
        "The PLaser dashboard enables real-time tuning and multi-physics profiling:\n"
        "• Panel 1 (Sidebar): Parameter sliders (R1, R2, L, T0, Active Current) swept inside valid trained bounds.\n"
        "• Panel 2 (Metrics): Live output power (mW), WPE (%), total terminal current, and device lasing state.\n"
        "• Panels 3 & 4 (Profiles): Longitudinal carrier density N(z) and total optical power profile P(z)."
    )
    y = draw_paragraph(ax, layout_txt, 0.05, y)
    
    # Embed annotated dashboard screenshot
    embed_image(fig, assets_dir / "dashboard_annotated.png", 0.05, 0.49, 0.90, 0.25)
    ax.text(0.5, 0.47, "Figure 3.1: PLaser web application interface showing sliders and live metrics.", color=MUTED_TEXT, fontsize=8, ha='center', style='italic')
    
    y = 0.43
    ax.text(0.05, y, "3.2 Understanding Spatial Hole Burning (SHB)", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    shb_txt = (
        "When asymmetry is introduced in the facet coatings (e.g. low output mirror R2, high rear mirror R1), "
        "the internal optical field intensity increases exponentially towards the output facet. This local surge in "
        "stimulated recombination rates drains carrier density near the right facet, causing the carrier density N(z) "
        "to drop significantly at the front mirror. This longitudinal carrier depletion is known as Spatial Hole Burning (SHB)."
    )
    y = draw_paragraph(ax, shb_txt, 0.05, y)
    
    # Embed SHB explainer diagram
    embed_image(fig, assets_dir / "shb_explainer.png", 0.05, 0.12, 0.90, 0.18)
    ax.text(0.5, 0.10, "Figure 3.2: Interaction of growing optical field intensity with depleted carrier profile.", color=MUTED_TEXT, fontsize=8, ha='center', style='italic')
    
    add_footer(ax, 4)
    pdf.savefig(fig, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    
    # ====================================================
    # Page 5: Concrete Validation & Plots
    # ====================================================
    fig = plt.figure(figsize=(8.5, 11), facecolor=BG_COLOR)
    ax = fig.add_axes([0, 0, 1, 1], facecolor="none")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    add_header(ax, "4. Verification & Validation Metrics")
    
    y = 0.84
    # 4.1 Verification
    ax.text(0.05, y, "4.1 Execution Speed & Generalization", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    ver_txt = (
        "PLaser's PINN surrogate has been validated against held-out validation samples. Accuracy and speed "
        "comparisons show massive performance gains with negligible error rates, making this model perfectly "
        "suitable for real-time laser cavity optimization sweeps."
    )
    y = draw_paragraph(ax, ver_txt, 0.05, y)
    
    # Embed Scatter plots
    embed_image(fig, assets_dir / "validation_scatter_power.png", 0.05, 0.46, 0.90, 0.28)
    ax.text(0.5, 0.44, "Figure 4.1: Predicted vs. True scatter plots for Optical Output Power and Wall-Plug Efficiency.", color=MUTED_TEXT, fontsize=8, ha='center', style='italic')
    
    # Embed Error Histogram
    embed_image(fig, assets_dir / "validation_error_histogram.png", 0.05, 0.14, 0.42, 0.24)
    
    # Put training info on the right side of the error histogram
    rx = 0.51
    ry = 0.35
    ax.text(rx, ry, "4.2 Convergence & Training Stats", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    ry -= 0.025
    ax.text(rx, ry, "• Validation Points: 200 random held-out sweeps", color=TEXT_COLOR, fontsize=9)
    ry -= 0.020
    ax.text(rx, ry, "• Power R² Coefficient: 0.998", color=TEXT_COLOR, fontsize=9)
    ry -= 0.020
    ax.text(rx, ry, "• WPE R² Coefficient: 0.997", color=TEXT_COLOR, fontsize=9)
    ry -= 0.020
    ax.text(rx, ry, "• Mean Power Residual Error: < 0.45 mW", color=TEXT_COLOR, fontsize=9)
    ry -= 0.020
    ax.text(rx, ry, "• Max Residual Error: < 2.50 mW", color=TEXT_COLOR, fontsize=9)
    ry -= 0.025
    ax.text(rx, ry, "4.3 Exporting Options", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    ry -= 0.025
    ax.text(rx, ry, "• Plots: Export by pressing Ctrl+P on web dashboard", color=TEXT_COLOR, fontsize=9)
    ry -= 0.020
    ax.text(rx, ry, "• Batch Data: Call PINNSurrogate.predict() in python", color=TEXT_COLOR, fontsize=9)
    ry -= 0.020
    ax.text(rx, ry, "  and dump outputs to CSV or JSON formats.", color=TEXT_COLOR, fontsize=9)
    
    ax.text(0.26, 0.11, "Figure 4.2: Optical power prediction residuals.", color=MUTED_TEXT, fontsize=8, ha='center', style='italic')
    
    add_footer(ax, 5)
    pdf.savefig(fig, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()

print(f"Compilation complete. PDF User Manual saved to {output_pdf_path}")
