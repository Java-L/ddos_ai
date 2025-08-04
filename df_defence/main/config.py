import os

from dl_ids.settings import MODELS_DIRS, MEAN_STD_DIRS

INTERFACE = r'\Device\NPF_{8FBD65D9-93B1-4B18-83DA-9A6D3FABB875}'
PORT = 80

# Define attack type mapping
ATTACK_MAPPING = {
    'DosFam': 'Distributed Denial of Service Attack',  # Optimized "DDoS Attack" to more formal expression
    'Heartbleed': 'Heartbleed Vulnerability Attack',
    'Infiltration': 'Internal Infiltration Attack',
    'Patator': 'Brute Force Attack',
    'PortScan': 'Port Scan Attack',
    'Bot': 'Botnet Attack',
    'WebAttack': 'Web Application Attack',
    'BENIGN': 'No Attack Detected'
}

# Attack type to threat level mapping (merged Web attacks and network attacks)
THREAT_MAPPING = {
    'Distributed Denial of Service Attack': 'High Risk',
    'Heartbleed Vulnerability Attack': 'High Risk',
    'Internal Infiltration Attack': 'High Risk',
    'Brute Force Attack': 'Medium Risk',
    'Port Scan Attack': 'Low Risk',
    'Botnet Attack': 'High Risk',
    'Web Application Attack': 'Medium Risk',
    'BENIGN': 'No Attack Detected'
}
# MODEL_TYPE = 'cnn'
MODEL_TYPE = 'lstm'
# MODEL_TYPE = 'cnn_lstm_attention'
STDS_PATH = os.path.join(MEAN_STD_DIRS, f"stds.txt")
MEANS_PATH = os.path.join(MEAN_STD_DIRS, f"means.txt")
CLASS_NAMES_PATH = os.path.join(MEAN_STD_DIRS, f"class_names.txt")
