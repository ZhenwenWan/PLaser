#!/usr/bin/env python3
"""
Train PINN Laser Model.
Generates a 2.5D dataset, trains a PyTorch Physics-Informed Neural Network (PINN)
surrogate model, and saves the trained weights.
"""

from __future__ import annotations
import sys
import math
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# Setup paths
RUN_DIR = Path(__file__).resolve().parent
REPO_DIR = RUN_DIR.parents[1]
TOOLS_DIR = REPO_DIR / "Tools"
DIAG_DIR = RUN_DIR / "diagnostics_laser_coupled"
DIAG_DIR.mkdir(parents=True, exist_ok=True)

# Enforce single-thread execution to prevent thread pool thrashing between NumPy and PyTorch
import os
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

# Add Libs and Tools to path



import torch
torch.set_num_threads(1)
import torch.nn as nn
import torch.optim as optim
from quasi_3d_synthesizer import Quasi3DSimulator

def generate_dataset(num_samples: int = 1500) -> tuple[np.ndarray, np.ndarray]:
    """Generates random parameter sweeps using the 2.5D solver."""
    print(f"Generating {num_samples} samples from the 2.5D solver...")
    
    np.random.seed(42)
    inputs = []
    targets = []
    
    # Ranges
    # R1: 0.1 to 0.95
    # R2: 0.05 to 0.5
    # L: 100 to 1000 um (0.01 to 0.1 cm)
    # T0: 250 to 360 K
    # I_active: 0.01 to 0.5 A
    
    count = 0
    while count < num_samples:
        R1 = np.random.uniform(0.1, 0.95)
        R2 = np.random.uniform(0.05, 0.5)
        L_um = np.random.uniform(100, 1000)
        L = L_um * 1e-4  # cm
        T0 = np.random.uniform(250, 360)
        I_active = np.random.uniform(0.01, 0.5)
        
        I_2d_unit = I_active / L
        
        sim = Quasi3DSimulator(L_cavity=L, R1=R1, R2=R2, M=51, T0=T0)
        
        try:
            res = sim.solve_longitudinal(I_2d_unit, verbose=False)
            P_opt = res["P_opt"]
            wpe = res["wpe"]
            I_total = res["I_total"]
            N_profile = res["N"]
            P_profile = res["P_plus"] + res["P_minus"]
            
            # Pack input: [R1, R2, L, T0, I_active]
            in_vec = [R1, R2, L, T0, I_active]
            
            # Pack output: [P_opt, wpe, I_total, 51-point N, 51-point P]
            out_vec = [P_opt, wpe, I_total] + list(N_profile) + list(P_profile)
            
            inputs.append(in_vec)
            targets.append(out_vec)
            count += 1
            
            if count % 200 == 0:
                print(f"  Generated {count}/{num_samples} samples...")
        except Exception as e:
            # Skip failed solver configurations
            continue
            
    return np.array(inputs), np.array(targets)

class PINNLaser(nn.Module):
    def __init__(self, input_dim=5, output_dim=105):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.GELU(),
            nn.Linear(128, 128),
            nn.GELU(),
            nn.Linear(128, 128),
            nn.GELU(),
            nn.Linear(128, output_dim),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        return self.net(x)

def train():
    inputs_path = RUN_DIR / "data" / "pinn_inputs.npy"
    targets_path = RUN_DIR / "data" / "pinn_targets.npy"
    if not inputs_path.exists() or not targets_path.exists():
        raise FileNotFoundError(
            f"Dataset files not found. Please run scratch/generate_dataset_standalone.py first!"
        )
    inputs = np.load(str(inputs_path))
    targets = np.load(str(targets_path))
    
    # Scale inputs/targets for better neural network training
    # We use manual scaling to keep scaling functions easy in client apps
    in_min = np.array([0.1, 0.05, 0.01, 250.0, 0.01])
    in_max = np.array([0.95, 0.5, 0.1, 360.0, 0.5])
    
    out_min = np.zeros(105)
    out_max = np.ones(105)
    out_max[0] = 1.0      # P_opt max ~1W
    out_max[1] = 0.5      # WPE max ~50%
    out_max[2] = 20.0     # I_total max ~20A
    out_max[3:54] = 1.0e19 # N profile max ~1e19
    out_max[54:105] = 20.0 # P profile max ~20W
    
    np.savez(
        str(RUN_DIR / "data" / "pinn_scale_params.npz"),
        in_min=in_min,
        in_max=in_max,
        out_min=out_min,
        out_max=out_max
    )
    
    scaled_inputs = (inputs - in_min) / (in_max - in_min)
    scaled_targets = (targets - out_min) / (out_max - out_min)
    
    # Tensors
    X_train = torch.FloatTensor(scaled_inputs)
    y_train = torch.FloatTensor(scaled_targets)
    
    # Model
    model = PINNLaser(5, 105)
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    
    # Constants for physics residuals
    q0 = 1.60213377e-19
    A_act = 2.8e-4 * 0.342e-4
    E_phot = 6.62607015e-34 * 1.934e14
    
    print("\nTraining the PINN model...")
    epochs = 150
    loss_history = []
    
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        
        pred = model(X_train)
        
        # 1. Data regression loss (MSE)
        loss_data = nn.MSELoss()(pred, y_train)
        
        # 2. Physics-informed loss (Carrier rate residuals)
        # Unscale variables for physics computation
        X_unscaled = X_train * torch.FloatTensor(in_max - in_min) + torch.FloatTensor(in_min)
        pred_unscaled = pred * torch.FloatTensor(out_max - out_min) + torch.FloatTensor(out_min)
        
        T0 = X_unscaled[:, 3]
        L = X_unscaled[:, 2]
        I_active = X_unscaled[:, 4]
        
        I_2d_unit = I_active / L
        G_inj = I_2d_unit / (q0 * A_act)
        
        # Temp scaling laws
        temp_gain_scale = torch.exp(-(T0 - 300.0) / 120.0)
        temp_ntr_scale = (T0 / 300.0)**1.5
        temp_auger_scale = (T0 / 300.0)**2.0
        
        g0_gain = 1200.0 * temp_gain_scale
        N_tr = 1.0e18 * temp_ntr_scale
        C_recomb = 3.0e-29 * temp_auger_scale
        
        A_recomb = 1.0e8
        B_recomb = 1.0e-10
        
        # Extrapolate over z grid (evaluate residual at a few nodes to conserve memory)
        # Let's check nodes 0, 12, 25, 37, 50
        nodes = [0, 12, 25, 37, 50]
        phys_residual = 0.0
        
        for k in nodes:
            N_node = pred_unscaled[:, 3 + k]
            P_node = pred_unscaled[:, 54 + k]
            
            # Scaled carrier density for numerical stability (in units of 1e18 cm^-3)
            N_scaled = N_node / 1.0e18
            N_tr_scaled = N_tr / 1.0e18
            
            # Logarithmic gain
            gain = g0_gain * (torch.log(torch.clamp(N_scaled / N_tr_scaled, min=1.0e-3)))
            gain = torch.clamp(gain, min=0.0)
            
            # Scaled recombination rates to prevent float32 overflow (up to 10^38 limit)
            # C_recomb * 1e54 = 3e-29 * temp_auger_scale * 1e54 = 30000 * temp_auger_scale
            C_recomb_scaled = 30000.0 * temp_auger_scale
            R_rec = (1.0e26 * N_scaled) + (1.0e26 * N_scaled**2) + C_recomb_scaled * N_scaled**3
            R_stim = (gain * P_node) / (A_act * E_phot)
            
            f_N = G_inj - R_rec - R_stim
            # Scale physics residual by G_inj order of magnitude to align scale
            phys_residual += torch.mean((f_N / 1.0e27)**2)
            
        loss_phys = phys_residual / len(nodes)
        
        # Combined loss
        loss = loss_data + 0.05 * loss_phys
        
        loss.backward()
        optimizer.step()
        
        loss_history.append(loss.item())
        if (epoch + 1) % 15 == 0:
            print(f"  Epoch {epoch+1:3d}/{epochs}: Loss = {loss.item():.6e} (Data={loss_data.item():.6e}, Phys={loss_phys.item():.6e})")
            
    # Save model weights
    torch.save(model.state_dict(), str(RUN_DIR / "models" / "pinn_laser_model.pt"))
    print("\nModel saved successfully as pinn_laser_model.pt")
    
    # Plot training loss
    plt.figure(figsize=(8, 5))
    plt.plot(loss_history, color="#64ffda", linewidth=2.5)
    plt.title("PINN Surrogate Training Loss", color="white", fontsize=13)
    plt.xlabel("Epoch", color="white")
    plt.ylabel("Loss", color="white")
    plt.grid(True, linestyle="--", alpha=0.3, color="#555555")
    plt.gca().set_facecolor("#1e1e1e")
    plt.gcf().patch.set_facecolor("#121212")
    plt.gca().tick_params(colors="white")
    for spine in plt.gca().spines.values():
        spine.set_color("#555555")
    plt.yscale("log")
    
    plot_path = RUN_DIR / "models" / "pinn_training_loss.svg"
    plt.savefig(plot_path, dpi=300, facecolor=plt.gcf().get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Saved training loss plot to {plot_path.name}")
    
    