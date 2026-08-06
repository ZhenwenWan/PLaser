#!/usr/bin/env python3
"""
PINN Surrogate Wrapper.
Loads the trained PyTorch model and scale parameters to perform instant predictions.
"""

from __future__ import annotations
import sys
from pathlib import Path
# Local libs import path removed
import numpy as np
import torch
import torch.nn as nn

# Define the model class (must match train_pinn.py)
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

class PINNSurrogate:
    def __init__(self, model_dir: Path):
        self.model_dir = model_dir
        
        # Load scale parameters
        scale_path = model_dir / "data" / "pinn_scale_params.npz" if (model_dir / "data").exists() else model_dir / "pinn_scale_params.npz"
        if not scale_path.exists():
            raise FileNotFoundError(f"Scale parameters not found at {scale_path}")
            
        data = np.load(str(scale_path))
        self.in_min = data["in_min"]
        self.in_max = data["in_max"]
        self.out_min = data["out_min"]
        self.out_max = data["out_max"]
        
        # Initialize and load model weights
        self.model = PINNLaser(5, 105)
        model_path = model_dir / "models" / "pinn_laser_model.pt" if (model_dir / "models").exists() else model_dir / "pinn_laser_model.pt"
        if not model_path.exists():
            raise FileNotFoundError(f"Model weights not found at {model_path}")
            
        self.model.load_state_dict(torch.load(str(model_path), map_location=torch.device('cpu')))
        self.model.eval()
        
    def predict(
        self,
        R1: float,
        R2: float,
        L_um: float,
        T0: float,
        I_active: float,
        w_active_um: float | None = None,
        d_active_um: float | None = None
    ) -> dict[str, np.ndarray | float]:
        """
        Instantly predicts laser performance metrics and profiles.
        R1, R2: reflectivities [0 to 1]
        L_um: cavity length in um
        T0: ambient temperature in K
        I_active: active region current in A
        w_active_um: optional custom ridge width in um (default 2.8)
        d_active_um: optional custom active thickness in um (default 0.342)
        """
        L = L_um * 1e-4  # cm
        
        w_ref = 2.8
        d_ref = 0.342
        
        if w_active_um is not None and d_active_um is not None:
            area_ratio = (w_active_um * d_active_um) / (w_ref * d_ref)
            w_ratio = w_active_um / w_ref
        else:
            area_ratio = 1.0
            w_ratio = 1.0
            
        # Scale current to maintain same carrier injection rate G_inj in reference model
        I_model_input = I_active / area_ratio
        
        # Input vector
        in_vec = np.array([R1, R2, L, T0, I_model_input], dtype=np.float32)
        
        # Scale
        scaled_in = (in_vec - self.in_min) / (self.in_max - self.in_min)
        scaled_in_tensor = torch.FloatTensor(scaled_in).unsqueeze(0)
        
        # Predict
        with torch.no_grad():
            scaled_out = self.model(scaled_in_tensor).numpy().squeeze(0)
            
        # Unscale
        out_vec = scaled_out * (self.out_max - self.out_min) + self.out_min
        
        # Parse output vector: [P_opt, wpe, I_total, 51-point N, 51-point P]
        P_opt_model = float(max(out_vec[0], 0.0))
        I_total_model = float(max(out_vec[2], 0.0))
        
        N_profile = np.clip(out_vec[3:54], a_min=1.0e15, a_max=None)
        P_profile_model = np.clip(out_vec[54:105], a_min=0.0, a_max=None)
        
        # Scale outputs according to area and width ratios
        P_opt = P_opt_model * area_ratio
        P_profile = P_profile_model * area_ratio
        
        # Shunt current scales with contact stripe width
        I_shunt_model = I_total_model - I_model_input
        I_total = I_active + I_shunt_model * w_ratio
        
        # Recalculate WPE based on scaled outputs
        V_bias = 1.0499
        P_elec = I_total * V_bias
        wpe = P_opt / P_elec if P_elec > 0.0 else 0.0
        
        z_grid = np.linspace(0.0, L_um, 51)
        
        return {
            "P_opt": P_opt,
            "wpe": wpe,
            "I_total": I_total,
            "N": N_profile,
            "P": P_profile,
            "z_grid": z_grid
        }
