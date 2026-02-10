"""
Synthetic Data Generator for MOF Electrochemical Performance
Generates physics-informed training data for GCD, IES, and EIS predictions
"""

import numpy as np
import pandas as pd
import json
from pathlib import Path

# Configuration
NUM_SAMPLES = 5000
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# Define parameter spaces
# Common metals - can be extended with any metal
METALS = ['Cu', 'Ni', 'Co', 'Zn', 'Fe', 'Mn', 'Ag', 'Au', 'Pd', 'Pt', 'Cr', 'V', 'Ti', 'Mo', 'W']
VALENCIES = [1, 2, 3]
LIGANDS = ['BDC', 'BTC', 'DOBDC', 'BPDC', 'NDC', 'TPA']
ASSEMBLIES = ['Two-Electrode', 'Three-Electrode']
ELECTRODES = ['Nickel Foam', 'Glassy Carbon', 'Carbon Cloth', 'Stainless Steel']
IS_MOF = [True, False]

# Physics-informed parameters - Extended metal database
METAL_PROPERTIES = {
    'Cu': {'redox_factor': 1.2, 'conductivity': 1.15, 'plasmon_peak': 22, 'd_transition': 5},
    'Ni': {'redox_factor': 1.1, 'conductivity': 1.10, 'plasmon_peak': 20, 'd_transition': 6},
    'Co': {'redox_factor': 1.15, 'conductivity': 1.12, 'plasmon_peak': 21, 'd_transition': 5.5},
    'Zn': {'redox_factor': 0.95, 'conductivity': 1.05, 'plasmon_peak': 19, 'd_transition': 7},
    'Fe': {'redox_factor': 1.05, 'conductivity': 1.08, 'plasmon_peak': 20.5, 'd_transition': 6.5},
    'Mn': {'redox_factor': 1.0, 'conductivity': 1.06, 'plasmon_peak': 19.5, 'd_transition': 6.8},
    'Ag': {'redox_factor': 1.25, 'conductivity': 1.20, 'plasmon_peak': 23, 'd_transition': 4.5},
    'Au': {'redox_factor': 1.18, 'conductivity': 1.18, 'plasmon_peak': 24, 'd_transition': 4.8},
    'Pd': {'redox_factor': 1.12, 'conductivity': 1.14, 'plasmon_peak': 21.5, 'd_transition': 5.2},
    'Pt': {'redox_factor': 1.22, 'conductivity': 1.17, 'plasmon_peak': 23.5, 'd_transition': 5.0},
    'Cr': {'redox_factor': 1.08, 'conductivity': 1.09, 'plasmon_peak': 20.2, 'd_transition': 6.2},
    'V': {'redox_factor': 1.06, 'conductivity': 1.07, 'plasmon_peak': 19.8, 'd_transition': 6.5},
    'Ti': {'redox_factor': 0.98, 'conductivity': 1.04, 'plasmon_peak': 18.5, 'd_transition': 7.2},
    'Mo': {'redox_factor': 1.13, 'conductivity': 1.11, 'plasmon_peak': 21.8, 'd_transition': 5.8},
    'W': {'redox_factor': 1.16, 'conductivity': 1.13, 'plasmon_peak': 22.5, 'd_transition': 5.5},
}

# Function to get metal properties (with default for unknown metals)
def get_metal_properties(metal):
    """Get metal properties, with defaults for unknown metals"""
    if metal in METAL_PROPERTIES:
        return METAL_PROPERTIES[metal]
    else:
        # Default properties based on periodic table position
        return {
            'redox_factor': 1.0,
            'conductivity': 1.0,
            'plasmon_peak': 20.0,
            'd_transition': 6.0
        }

ELECTRODE_PROPERTIES = {
    'Nickel Foam': {'capacity_boost': 1.3, 'resistance': 0.8},
    'Glassy Carbon': {'capacity_boost': 1.0, 'resistance': 1.0},
    'Carbon Cloth': {'capacity_boost': 1.15, 'resistance': 0.9},
    'Stainless Steel': {'capacity_boost': 1.1, 'resistance': 1.1},
}

LIGAND_PROPERTIES = {
    'BDC': {'porosity': 1.1, 'stability': 1.0},
    'BTC': {'porosity': 1.2, 'stability': 1.1},
    'DOBDC': {'porosity': 1.15, 'stability': 1.05},
    'BPDC': {'porosity': 1.05, 'stability': 0.95},
    'NDC': {'porosity': 1.08, 'stability': 1.02},
    'TPA': {'porosity': 1.12, 'stability': 1.08},
}

def generate_gcd_curve(params):
    """Generate Galvanostatic Charge-Discharge curve data"""
    current_densities = np.array([0.5, 1.0, 1.5, 2.0, 2.5])
    
    # Base parameters
    metal = params['metal']
    valency = params['valency']
    is_mof = params['is_mof']
    electrode = params['electrode']
    ligand = params['ligand']
    assembly = params['assembly']
    
    # Calculate capacity multiplier
    base_capacity = 100 * valency  # mAh/g
    metal_props = get_metal_properties(metal)
    metal_factor = metal_props['redox_factor']
    electrode_factor = ELECTRODE_PROPERTIES[electrode]['capacity_boost']
    ligand_factor = LIGAND_PROPERTIES[ligand]['porosity']
    mof_factor = 1.5 if is_mof else 1.0
    assembly_factor = 1.1 if assembly == 'Three-Electrode' else 1.0
    
    capacity_multiplier = metal_factor * electrode_factor * ligand_factor * mof_factor * assembly_factor
    
    # Generate discharge curves for each current density
    gcd_data = {}
    for i, current in enumerate(current_densities):
        # Time points (0 to max discharge time)
        max_time = (base_capacity * capacity_multiplier) / (current * 60)  # hours
        time = np.linspace(0, max_time, 200)
        
        # Voltage decay (exponential with some noise)
        V_start = 0.9 + 0.1 * np.random.random()
        V_end = 0.1 + 0.05 * np.random.random()
        voltage = V_end + (V_start - V_end) * np.exp(-time / (max_time / 3))
        voltage += np.random.normal(0, 0.01, len(time))  # Add noise
        
        gcd_data[f'current_{current}'] = {
            'time': time.tolist(),
            'voltage': voltage.tolist()
        }
    
    return gcd_data

def generate_rate_capability(params):
    """Generate Rate Capability data (specific capacity vs current density)"""
    current_densities = np.linspace(0.5, 5.0, 10)
    
    # Base parameters
    metal = params['metal']
    valency = params['valency']
    is_mof = params['is_mof']
    electrode = params['electrode']
    ligand = params['ligand']
    
    # Calculate base capacity
    base_capacity = 100 * valency
    metal_factor = METAL_PROPERTIES[metal]['redox_factor']
    electrode_factor = ELECTRODE_PROPERTIES[electrode]['capacity_boost']
    ligand_factor = LIGAND_PROPERTIES[ligand]['porosity']
    mof_factor = 1.5 if is_mof else 1.0
    
    max_capacity = base_capacity * metal_factor * electrode_factor * ligand_factor * mof_factor
    
    # Capacity decay with increasing current (power law)
    capacity = max_capacity * (0.5 / current_densities)**0.3
    capacity += np.random.normal(0, max_capacity * 0.02, len(capacity))  # Add noise
    capacity = np.clip(capacity, 0, max_capacity)
    
    return {
        'current_density': current_densities.tolist(),
        'specific_capacity': capacity.tolist()
    }

def generate_ies_spectrum(params):
    """Generate Inelastic Electron Scattering spectrum"""
    energy = np.linspace(0, 50, 500)
    
    metal = params['metal']
    metal_props = get_metal_properties(metal)
    
    # Bulk plasmon peak (Gaussian)
    plasmon_energy = metal_props['plasmon_peak']
    plasmon_intensity = 0.8 + 0.2 * np.random.random()
    plasmon_width = 2.0 + 0.5 * np.random.random()
    
    plasmon_peak = plasmon_intensity * np.exp(-((energy - plasmon_energy) / plasmon_width)**2)
    
    # d-d transition peak (lower energy)
    d_transition_energy = metal_props['d_transition']
    d_intensity = 0.4 + 0.1 * np.random.random()
    d_width = 1.5 + 0.3 * np.random.random()
    
    d_peak = d_intensity * np.exp(-((energy - d_transition_energy) / d_width)**2)
    
    # Background (slowly decaying)
    background = 0.1 * np.exp(-energy / 30)
    
    # Total spectrum
    spectrum = plasmon_peak + d_peak + background
    spectrum += np.random.normal(0, 0.01, len(energy))  # Add noise
    spectrum = np.clip(spectrum, 0, None)
    
    return {
        'energy': energy.tolist(),
        'intensity': spectrum.tolist()
    }

def generate_eis_nyquist(params):
    """Generate Electrochemical Impedance Spectroscopy Nyquist plot"""
    # Frequency range (log scale)
    freq = np.logspace(-2, 5, 100)
    
    metal = params['metal']
    electrode = params['electrode']
    
    # Calculate resistance parameters
    R_solution = 5 + 2 * np.random.random()  # Ohm
    R_ct = ELECTRODE_PROPERTIES[electrode]['resistance'] * (20 + 10 * np.random.random())
    CPE_T = 0.001 + 0.0005 * np.random.random()
    CPE_P = 0.85 + 0.1 * np.random.random()
    W = 10 + 5 * np.random.random()  # Warburg coefficient
    
    # Calculate complex impedance
    omega = 2 * np.pi * freq
    
    # CPE impedance
    Z_CPE = 1 / (CPE_T * (1j * omega)**CPE_P)
    
    # Warburg impedance (low frequency)
    Z_W = W / np.sqrt(omega) * (1 - 1j)
    
    # Total impedance (simplified Randles circuit)
    Z_total = R_solution + 1 / (1/R_ct + 1/(Z_CPE + Z_W))
    
    Z_real = np.real(Z_total)
    Z_imag = -np.imag(Z_total)  # Negative for conventional plotting
    
    # Add noise
    Z_real += np.random.normal(0, 0.5, len(Z_real))
    Z_imag += np.random.normal(0, 0.5, len(Z_imag))
    
    return {
        'z_real': Z_real.tolist(),
        'z_imag': Z_imag.tolist(),
        'frequency': freq.tolist()
    }

def generate_sample():
    """Generate a single synthetic sample"""
    # Random parameters
    params = {
        'metal': np.random.choice(METALS),
        'valency': np.random.choice(VALENCIES),
        'ligand': np.random.choice(LIGANDS),
        'assembly': np.random.choice(ASSEMBLIES),
        'electrode': np.random.choice(ELECTRODES),
        'is_mof': np.random.choice(IS_MOF)
    }
    
    # Generate all outputs
    sample = {
        'inputs': params,
        'outputs': {
            'gcd': generate_gcd_curve(params),
            'rate_capability': generate_rate_capability(params),
            'ies': generate_ies_spectrum(params),
            'eis': generate_eis_nyquist(params)
        }
    }
    
    return sample

def create_feature_vector(params):
    """Convert categorical parameters to numerical features"""
    features = []
    
    # One-hot encode metal
    for metal in METALS:
        features.append(1.0 if params['metal'] == metal else 0.0)
    
    # Valency (normalized)
    features.append(params['valency'] / 3.0)
    
    # One-hot encode ligand
    for ligand in LIGANDS:
        features.append(1.0 if params['ligand'] == ligand else 0.0)
    
    # One-hot encode assembly
    features.append(1.0 if params['assembly'] == 'Three-Electrode' else 0.0)
    
    # One-hot encode electrode
    for electrode in ELECTRODES:
        features.append(1.0 if params['electrode'] == electrode else 0.0)
    
    # Is MOF
    features.append(1.0 if params['is_mof'] else 0.0)
    
    return features

def main():
    """Generate synthetic dataset"""
    print("Generating synthetic MOF performance data...")
    print(f"Target samples: {NUM_SAMPLES}")
    
    # Create output directory
    output_dir = Path('/home/claude/mof_data')
    output_dir.mkdir(exist_ok=True)
    
    # Generate samples
    dataset = []
    feature_data = []
    
    for i in range(NUM_SAMPLES):
        if (i + 1) % 500 == 0:
            print(f"Generated {i + 1}/{NUM_SAMPLES} samples...")
        
        sample = generate_sample()
        dataset.append(sample)
        
        # Create feature row for tabular export
        features = create_feature_vector(sample['inputs'])
        feature_row = sample['inputs'].copy()
        feature_row['features'] = features
        feature_data.append(feature_row)
    
    # Save complete dataset as JSON
    output_file = output_dir / 'synthetic_dataset.json'
    with open(output_file, 'w') as f:
        json.dump(dataset, f, indent=2)
    print(f"\nSaved complete dataset to {output_file}")
    
    # Save feature summary as CSV
    df = pd.DataFrame(feature_data)
    csv_file = output_dir / 'feature_summary.csv'
    df.to_csv(csv_file, index=False)
    print(f"Saved feature summary to {csv_file}")
    
    # Print statistics
    print("\n=== Dataset Statistics ===")
    print(f"Total samples: {len(dataset)}")
    print(f"Input dimension: {len(features)}")
    print("\nParameter distribution:")
    for key in ['metal', 'valency', 'ligand', 'assembly', 'electrode', 'is_mof']:
        values = [s['inputs'][key] for s in dataset]
        unique, counts = np.unique(values, return_counts=True)
        print(f"\n{key}:")
        for val, count in zip(unique, counts):
            print(f"  {val}: {count} ({100*count/len(dataset):.1f}%)")
    
    print("\n✓ Data generation complete!")

if __name__ == "__main__":
    main()
