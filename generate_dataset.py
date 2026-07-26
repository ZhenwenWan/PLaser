import sys
import math
from pathlib import Path
import numpy as np


from quasi_3d_synthesizer import Quasi3DSimulator

np.random.seed(42)
count = 0
num_samples = 1500
inputs = []
targets = []

print("Starting standalone dataset generation...")
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
        wpe = res["WPE"]
        I_total = res["I_total"]
        N_profile = res["N"]
        P_profile = res["P_plus"] + res["P_minus"]
        
        in_vec = [R1, R2, L, T0, I_active]
        out_vec = [P_opt, wpe, I_total] + list(N_profile) + list(P_profile)
        
        inputs.append(in_vec)
        targets.append(out_vec)
        count += 1
        
        if count % 300 == 0:
            print(f"Generated {count}/{num_samples}...")
    except Exception as e:
        continue

# Save to App/Run
out_dir = Path(__file__).resolve().parent / "data"
np.save(str(out_dir / "pinn_inputs.npy"), inputs)
np.save(str(out_dir / "pinn_targets.npy"), targets)
print("Dataset generation completed and saved successfully!")
