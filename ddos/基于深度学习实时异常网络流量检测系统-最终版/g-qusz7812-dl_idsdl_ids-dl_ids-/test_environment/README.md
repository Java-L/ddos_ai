# Deep Learning Network Traffic Anomaly Detection System - Attack-Defense Environment Testing

This directory contains attack-defense environment scripts for testing the deep learning network traffic anomaly detection system.

## File Description

### 1. `run_test.py` - Main Test Script
Complete attack-defense environment test startup script that automates the entire testing process.

**Features:**
- Automatically start Django server
- Wait for user confirmation of readiness
- Start attack simulator
- Monitor system status
- Display test results

**Usage:**
```bash
cd test_environment
python run_test.py
```

### 2. `attack_simulator.py` - Attack Simulator
Simulates various network attack types to test the effectiveness of the detection system.

**Supported Attack Types:**
- **DoS Attack**: TCP SYN Flood attack
- **Port Scan**: TCP SYN port scanning
- **Web Attack**: SQL injection, XSS, path traversal, etc.
- **Botnet**: Simulate C&C communication and data exfiltration
- **Infiltration Attack**: Brute force, file upload, etc.

**Usage:**
```bash
# Execute all attack types
python attack_simulator.py --attack all

# Execute specific attacks
python attack_simulator.py --attack dos
python attack_simulator.py --attack scan
python attack_simulator.py --attack web

# Specify target
python attack_simulator.py --target 192.168.1.100 --port 8080

# Generate normal traffic simultaneously
python attack_simulator.py --attack all --normal
```

### 3. `traffic_generator.py` - Traffic Generator
Generates various types of network traffic, including normal traffic and specific attack traffic.

**Supported Traffic Types:**
- **Normal Traffic**: Simulate normal user behavior
- **Heartbleed**: Simulate Heartbleed vulnerability attack
- **Patator**: Simulate brute force attack
- **Infiltration**: Simulate infiltration attack

**Usage:**
```bash
# Generate all types of traffic
python traffic_generator.py --type all --duration 120

# Generate specific type of traffic
python traffic_generator.py --type benign --duration 60
python traffic_generator.py --type heartbleed --duration 30
python traffic_generator.py --type patator --duration 45

# Specify target and port
python traffic_generator.py --target 127.0.0.1 --port 8000 --type all
```

## Quick Start

### 1. Environment Setup
Ensure all dependencies are installed:
```bash
pip install django requests scapy torch numpy pandas
```

### 2. Start Complete Test
```bash
cd test_environment
python run_test.py
```

### 3. Manual Testing Steps

If you want to manually control the testing process:

**Step 1: Start Django Server**
```bash
cd ..  # Return to project root directory
python manage.py runserver 127.0.0.1:8000
```

**Step 2: Login to Admin Backend**
- Access: http://127.0.0.1:8000/admin/
- Username: admin
- Password: admin

**Step 3: Run Attack Simulation**
```bash
cd test_environment
python attack_simulator.py --attack all --normal
```

**Step 4: View Detection Results**
- Traffic Logs: http://127.0.0.1:8000/admin/main/trafficlog/
- IP Rules: http://127.0.0.1:8000/admin/main/ipaddressrule/
- Tuning Models: http://127.0.0.1:8000/admin/main/tuningmodels/

## Test Scenarios

### Scenario 1: Basic Function Test
```bash
# Generate normal traffic for 30 seconds
python traffic_generator.py --type benign --duration 30

# Then execute DoS attack
python attack_simulator.py --attack dos
```

### Scenario 2: Mixed Attack Test
```bash
# Generate normal traffic and various attacks simultaneously
python attack_simulator.py --attack all --normal
```

### Scenario 3: Specific Attack Type Test
```bash
# Test Web attack detection
python attack_simulator.py --attack web

# Test port scan detection
python attack_simulator.py --attack scan

# Test botnet detection
python attack_simulator.py --attack bot
```

## Viewing Detection Results

### 1. Real-time Monitoring
View real-time detection logs in Django server terminal output:
- Model loading information
- Network packet capture information
- Anomaly detection results

### 2. Web Interface View
Access admin backend to view detailed results:
- **Traffic Logs**: Record all detected network traffic
- **Attack Types**: Display detected attack classifications
- **Threat Levels**: Display threat assessment results
- **IP Rules**: View blacklist and whitelist rules

### 3. Database View
Directly view SQLite database file:
```bash
sqlite3 db.sqlite3
.tables
SELECT * FROM tb_packetbaseinfo LIMIT 10;
```

## Important Notes

### 1. Permission Requirements
- Some attack simulations require administrator privileges (such as raw sockets)
- May need to run as administrator on Windows
- May need sudo privileges on Linux

### 2. Firewall Settings
- Ensure firewall does not block test traffic
- Some attacks may trigger security software alerts

### 3. Network Environment
- Recommended to run in isolated test environment
- Do not execute attack tests in production environment

### 4. Performance Considerations
- Attack simulation will generate large amounts of network traffic
- Ensure system has sufficient resources to handle detection tasks

## Troubleshooting

### 1. Django Server Startup Failure
```bash
# Check if port is occupied
netstat -an | grep 8000

# Check database migration
python manage.py migrate

# Check dependency installation
pip list | grep django
```

### 2. Attack Simulation Failure
```bash
# Check network connection
ping 127.0.0.1

# Check scapy permissions
python -c "from scapy.all import *; print('Scapy OK')"

# Check target port
telnet 127.0.0.1 8000
```

### 3. Empty Detection Results
- Ensure network monitoring components are running properly
- Check if model files are loaded correctly
- View Django log output

## Extended Features

### 1. Custom Attacks
You can modify `attack_simulator.py` to add new attack types:
```python
def custom_attack(self, duration=30):
    """Custom attack"""
    # Implement custom attack logic
    pass
```

### 2. Custom Traffic
You can modify `traffic_generator.py` to add new traffic patterns:
```python
def generate_custom_traffic(self, duration=60):
    """Generate custom traffic"""
    # Implement custom traffic generation logic
    pass
```

### 3. Result Analysis
You can add automated result analysis scripts:
```python
def analyze_results():
    """Analyze detection results"""
    # Read results from database
    # Generate statistical reports
    # Calculate detection accuracy
    pass
```

## Contact Information

For questions or suggestions, please contact the development team.
