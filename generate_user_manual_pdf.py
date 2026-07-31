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

def draw_paragraph(ax, text, x, y, max_len=100, line_height=0.019, color="#e6f1ff", fontsize=9.2):
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
    # Page 1: Cover Page
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
    # Page 2: Device Architecture & Mapping (4 Panels)
    # ====================================================
    fig = plt.figure(figsize=(8.5, 11), facecolor=BG_COLOR)
    ax = fig.add_axes([0, 0, 1, 1], facecolor="none")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    add_header(ax, "1. Device Architecture & Solver Mapping")
    
    y = 0.84
    # Panel 1
    ax.text(0.05, y, "Panel 1: Physical Device Assembly (Butterfly Package & Diode Chip)", color=ACCENT_GREEN, fontsize=10.5, fontweight="bold")
    y -= 0.02
    p1_txt = (
        "In fiber-optic telecommunications, edge-emitting semiconductor lasers are integrated into standard 14-Pin "
        "Butterfly Packages. The laser chip itself is a micron-scale semiconductor grown on InP substrates, "
        "injecting current through stripe contacts to generate gain inside a Multi-Quantum Well (MQW) active layer."
    )
    y = draw_paragraph(ax, p1_txt, 0.05, y)
    
    # Panel 2
    y -= 0.01
    ax.text(0.05, y, "Panel 2: Submount Heat Sink (Submount Mounting & Heat Dissipation)", color=ACCENT_GREEN, fontsize=10.5, fontweight="bold")
    y -= 0.02
    p2_txt = (
        "To prevent thermal droop, the laser chip is mounted p-side down on highly conductive Copper (Cu) or SiC "
        "submounts. This configuration provides the shortest thermal path to remove self-heating. The bottom of "
        "the submount is clamped to the coolant temperature T0, acting as a thermal boundary sink."
    )
    y = draw_paragraph(ax, p2_txt, 0.05, y)

    # Panel 3
    y -= 0.01
    ax.text(0.05, y, "Panel 3: 2D Transverse Model (2D Elmer FEM Cross-Section Solver)", color=ACCENT_GREEN, fontsize=10.5, fontweight="bold")
    y -= 0.02
    p3_txt = (
        "The 2D transverse plane cross-section governs optical waveguide modal confinement and localized physics. "
        "The reference 2D Elmer FEM solver solves the coupled Poisson (electrostatics), drift-diffusion (carriers), "
        "vector Helmholtz (wave optics), and thermal diffusion differential equations across the ridge cross-section."
    )
    y = draw_paragraph(ax, p3_txt, 0.05, y)

    # Panel 4
    y -= 0.01
    ax.text(0.05, y, "Panel 4: 1D Longitudinal Cavity & Spatial Hole Burning (SHB)", color=ACCENT_GREEN, fontsize=10.5, fontweight="bold")
    y -= 0.02
    p4_txt = (
        "Along the propagation z-axis, forward- and backward-propagating wave envelopes bounce between mirror facets. "
        "In asymmetric cavity coatings, the internal optical power increases exponentially towards the output facet, "
        "draining carrier density N(z) near the front mirror (SHB depletion dip), which impairs wavelength stability."
    )
    y = draw_paragraph(ax, p4_txt, 0.05, y)
    
    # Embed three parallel slicing images
    embed_image(fig, assets_dir / "3d_live_laser_chip.jpg", 0.05, 0.14, 0.28, 0.16)
    embed_image(fig, assets_dir / "3d_transparent_transverse_slice.jpg", 0.36, 0.14, 0.28, 0.16)
    embed_image(fig, assets_dir / "3d_transparent_longitudinal_slice.jpg", 0.67, 0.14, 0.28, 0.16)
    ax.text(0.5, 0.10, "Figure 1.1: Slicing the 3D physical laser chip (a) into transverse (b) and longitudinal (c) models.", color=MUTED_TEXT, fontsize=8, ha='center', style='italic')
    
    add_footer(ax, 2)
    pdf.savefig(fig, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    
    # ====================================================
    # Page 3: Application View Modes (2 Modes)
    # ====================================================
    fig = plt.figure(figsize=(8.5, 11), facecolor=BG_COLOR)
    ax = fig.add_axes([0, 0, 1, 1], facecolor="none")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    add_header(ax, "2. Application View Modes & Dashboards")
    
    y = 0.84
    # View Mode 1
    ax.text(0.05, y, "View Mode 1: Multi-Physics Dashboard", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    m1_txt = (
        "Provides a global coupled multi-physics overview. The left sidebar contains parameter control sliders "
        "(mirror coatings R1/R2, cavity length L, temperature T0, and injection current). The right main panel "
        "displays 6 synchronized viewports: longitudinal carrier density N(z), longitudinal optical power P(z), "
        "2D transverse optical waveguide mode, 2D temperature distribution, and horizontal/vertical cutlines. "
        "A lasing metrics card details the output power, efficiency, total current, and threshold state."
    )
    y = draw_paragraph(ax, m1_txt, 0.05, y)
    
    # View Mode 2
    y -= 0.015
    ax.text(0.05, y, "View Mode 2: 3D Cavity Field Analyzer", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    m2_txt = (
        "Focuses on local cross-sections along the cavity axis. The left sidebar features a cavity position slider "
        "to inspect local z (0 to L) alongside a compact card showing local carrier density N(z) and local optical "
        "power P(z). The right panel shows local 2D slices at the selected position and side-by-side flat 3D surface "
        "plots displaying the lateral-longitudinal (x-z plane) optical intensity envelope and thermal landscape."
    )
    y = draw_paragraph(ax, m2_txt, 0.05, y)
    
    # Embed annotated dashboard screenshot
    embed_image(fig, assets_dir / "dashboard_annotated.png", 0.05, 0.12, 0.90, 0.28)
    ax.text(0.5, 0.11, "Figure 2.1: Multi-physics dashboard view displaying six synchronized spatial output viewports.", color=MUTED_TEXT, fontsize=8, ha='center', style='italic')
    
    add_footer(ax, 3)
    pdf.savefig(fig, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    
    # ====================================================
    # Page 4: Installation & Onboarding Guide
    # ====================================================
    fig = plt.figure(figsize=(8.5, 11), facecolor=BG_COLOR)
    ax = fig.add_axes([0, 0, 1, 1], facecolor="none")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    add_header(ax, "3. Installation & Onboarding Guide")
    
    y = 0.84
    # 3.1 Environment Setup
    ax.text(0.05, y, "3.1 Local Environment Setup & Launch", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    setup_txt = (
        "Setup a virtual environment in a short folder path to avoid path length limits (WinError 206):\n"
        "  git clone https://github.com/ZhenwenWan/PLaser.git\n"
        "  cd PLaser\n"
        "  python -m venv .venv\n"
        "  .\\.venv\\Scripts\\Activate.ps1   # Windows activation\n"
        "  pip install -r requirements.txt\n\n"
        "Launch the Streamlit web application using pre-bundled weights:\n"
        "  python -m streamlit run app.py"
    )
    y = draw_paragraph(ax, setup_txt, 0.05, y)
    
    # 3.2 Optional tasks
    y -= 0.015
    ax.text(0.05, y, "3.2 Optional Execution Tasks", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    tasks_txt = (
        "• Regenerate sweeps dataset: python generate_dataset.py  [sweeps 1,500 physical cases]\n"
        "• Retrain PINN surrogate model: python train_pinn.py  [enforces physics loss in < 3 seconds]\n"
        "• Generate sweep video demo: python generate_animation.py  [compiles demonstration MP4 video]"
    )
    y = draw_paragraph(ax, tasks_txt, 0.05, y)
    
    # 3.3 Troubleshooting Table
    y -= 0.015
    ax.text(0.05, y, "3.3 Troubleshooting & Resolution Guide", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    
    table_data = [
        ["Symptom", "Likely Cause", "Action/Fix"],
        ["ModuleNotFoundError", "Virtual environment not active", "Run activation script then reinstall requirements"],
        ["Streamlit Model Missing", "Missing pt or npz weights file", "Run train_pinn.py to generate models/pinn_laser_model.pt"],
        ["WinError 206 / Path too long", "Windows filepath limit exceeded", "Move PLaser folder to C:\\PLaser and execute there"],
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
        table_y -= 0.035
        
    add_footer(ax, 4)
    pdf.savefig(fig, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    
    # ====================================================
    # Page 5: Verification & Validation
    # ====================================================
    fig = plt.figure(figsize=(8.5, 11), facecolor=BG_COLOR)
    ax = fig.add_axes([0, 0, 1, 1], facecolor="none")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    add_header(ax, "4. Verification & Validation Metrics")
    
    y = 0.84
    ax.text(0.05, y, "4.1 Execution Speed & Numerical Reference Accuracy", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    
    # Speed table
    speed_data = [
        ["Solver mode", "Execution Latency", "Accuracy (R2)", "EDA Role"],
        ["Elmer 2D FEM", "12 - 25 seconds", "1.000 (Ref)", "Waveguide Mode Profiling"],
        ["2.5D shooting solver", "1.2 - 2.8 seconds", "1.000 (Ref)", "Dataset sweeps"],
        ["PLaser PINN Surrogate", "< 5 milliseconds", "> 0.997", "Real-time interactive sweeps"]
    ]
    
    table_y = y
    for i, row in enumerate(speed_data):
        row_color = ACCENT_GREEN if i == 0 else "#ffffff"
        font_wt = "bold" if i == 0 else "normal"
        if i == 0:
            rect = plt.Rectangle((0.05, table_y - 0.005), 0.90, 0.025, facecolor=PANEL_COLOR, transform=ax.transAxes)
            ax.add_patch(rect)
        
        ax.text(0.06, table_y, row[0], color=row_color, fontsize=8, fontweight=font_wt, transform=ax.transAxes)
        ax.text(0.26, table_y, row[1], color=row_color, fontsize=8, fontweight=font_wt, transform=ax.transAxes)
        ax.text(0.48, table_y, row[2], color=row_color, fontsize=8, fontweight=font_wt, transform=ax.transAxes)
        ax.text(0.68, table_y, row[3], color=row_color, fontsize=8, fontweight=font_wt, transform=ax.transAxes)
        table_y -= 0.03
        
    y = table_y - 0.015
    ax.text(0.05, y, "4.2 Validation Scatter Plots & PINN Convergence", color=ACCENT_GREEN, fontsize=11, fontweight="bold")
    y -= 0.022
    val_txt = (
        "Verification scatter plots demonstrate excellent generalization metrics. Backpropagation training "
        "converges both target data errors and physics continuity residuals over 6 orders of magnitude."
    )
    y = draw_paragraph(ax, val_txt, 0.05, y)
    
    # Embed validation plots
    embed_image(fig, assets_dir / "validation_scatter_power.png", 0.05, 0.12, 0.50, 0.22)
    embed_image(fig, assets_dir / "pinn_training_loss.svg", 0.58, 0.12, 0.37, 0.22)
    
    ax.text(0.30, 0.10, "Figure 4.1: Predicted vs. True scatter alignment.", color=MUTED_TEXT, fontsize=7.5, ha='center', style='italic')
    ax.text(0.76, 0.10, "Figure 4.2: 6-order convergence loss.", color=MUTED_TEXT, fontsize=7.5, ha='center', style='italic')
    
    add_footer(ax, 5)
    pdf.savefig(fig, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()

print(f"Compilation complete. PDF User Manual saved to {output_pdf_path}")
