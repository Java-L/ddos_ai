# Deep Learning Network Traffic Anomaly Detection System

A Django-based deep learning system for detecting network traffic anomalies and DDoS attacks using CNN, LSTM, and attention mechanisms.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Windows/Linux/macOS
- Administrator privileges (for network packet capture)

### 1. Install Dependencies
```bash
# Install from requirements file
pip install -r requirements.txt

# Or install manually
pip install django==5.1.4 torch torchvision numpy pandas matplotlib seaborn scikit-learn scapy requests django-simple-captcha
```

### 2. Setup Database
```bash
cd df_defence
python manage.py migrate
python manage.py collectstatic --noinput
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
# Follow prompts to create admin account
```

### 4. Start the Application
```bash
python manage.py runserver 127.0.0.1:8000
```

### 5. Access the System
- **Main Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Traffic Logs**: http://127.0.0.1:8000/traffic-log/

## 🏗️ System Architecture

### Core Components
- **DDoS Detection Middleware**: Real-time traffic analysis and attack detection
- **Deep Learning Models**: CNN, LSTM, and CNN-LSTM-Attention models for classification
- **Traffic Monitor**: Network packet capture and feature extraction
- **Web Interface**: Django-based management and visualization

### Supported Attack Types
- **DoS/DDoS**: Denial of Service attacks
- **Port Scan**: Network reconnaissance
- **Web Attacks**: SQL injection, XSS, path traversal
- **Botnet**: C&C communication patterns
- **Infiltration**: Brute force and penetration attempts
- **Heartbleed**: SSL/TLS vulnerability exploitation

## 🧪 Testing Environment

### Automated Testing
```bash
# Run complete attack-defense test
cd test_environment
python run_test.py
```

### Manual Attack Simulation
```bash
# Simulate all attack types
python attack_simulator.py --attack all --normal

# Specific attack types
python attack_simulator.py --attack dos
python attack_simulator.py --attack scan
python attack_simulator.py --attack web

# Custom target
python attack_simulator.py --target 192.168.1.100 --port 8080
```

### Traffic Generation
```bash
# Generate mixed traffic
python traffic_generator.py --type all --duration 120

# Normal traffic only
python traffic_generator.py --type benign --duration 60
```

### Windows Quick Start
```batch
# Double-click or run in command prompt
test_environment\start_test.bat
```

## 📊 Model Management

### Available Models
- **CNN Model**: Convolutional Neural Network for spatial feature extraction
- **LSTM Model**: Long Short-Term Memory for temporal pattern recognition
- **CNN-LSTM-Attention**: Hybrid model with attention mechanism

### Model Training & Tuning
```bash
# Access model tuning interface
http://127.0.0.1:8000/model-tuning/

# Train new models with custom datasets
# Adjust hyperparameters through web interface
# Monitor training progress and metrics
```

## 🔍 Monitoring & Analysis

### Real-time Detection
- Live traffic monitoring through DDoS middleware
- Automatic threat classification and scoring
- Real-time alerts for high-risk activities

### Result Analysis
```bash
# Analyze detection results
cd test_environment
python analyze_results.py --hours 24 --show

# Generate detailed reports
python analyze_results.py --db ../db.sqlite3
```

### Web Dashboard
- **Traffic Logs**: http://127.0.0.1:8000/admin/main/trafficlog/
- **IP Rules**: http://127.0.0.1:8000/admin/main/ipaddressrule/
- **Model Status**: http://127.0.0.1:8000/admin/main/tuningmodels/

## 🛠️ Configuration

### Django Settings
Key configuration files:
- `df_defence/dl_ids/settings.py` - Main Django settings
- `df_defence/main/config.py` - Application-specific config
- `df_defence/main/ddos_middleware.py` - Detection parameters

### Detection Thresholds
```python
# Modify in ddos_middleware.py
RATE_LIMIT_THRESHOLD = 100  # Requests per minute
BURST_THRESHOLD = 20        # Burst requests in 10 seconds
CONNECTION_LIMIT = 50       # Max concurrent connections
```

### Model Paths
```python
# Model files location
df_defence/model/
├── best_model_cnn.pth
├── best_model_lstm.pth
└── best_model_cnn_lstm_attention.pth
```

## 🚨 Security Considerations

### Testing Environment
- **Use isolated networks** for attack simulation
- **Do not test on production systems**
- **Ensure proper authorization** before testing

### Legal Compliance
- Only test on systems you own or have explicit permission
- Follow local cybersecurity laws and regulations
- Document all testing activities

### Network Impact
- Attack simulations generate significant traffic
- May trigger security alerts in monitoring systems
- Ensure adequate system resources

## 🔧 Troubleshooting

### Common Issues

#### Django Server Won't Start
```bash
# Check port availability
netstat -an | grep 8000

# Verify database setup
python manage.py migrate
python manage.py check

# Test basic Django installation
python -c "import django; print(django.get_version())"
```

#### Permission Errors (Scapy)
```bash
# Windows: Run as Administrator
# Linux/macOS: Use sudo
sudo python manage.py runserver 127.0.0.1:8000

# Or install WinPcap/Npcap on Windows
# Install libpcap-dev on Linux
```

#### Missing Dependencies
```bash
# Reinstall requirements
pip install -r requirements.txt

# Check specific packages
python -c "import torch; print('PyTorch OK')"
python -c "from scapy.all import *; print('Scapy OK')"
```

#### No Detection Results
1. Check middleware is loaded in `settings.py`
2. Verify model files exist in `model/` directory
3. Ensure traffic is reaching the Django server
4. Check Django logs for errors

### Performance Issues
- **High CPU usage**: Reduce detection frequency or model complexity
- **Memory leaks**: Restart server periodically during heavy testing
- **Slow response**: Check database performance and indexing

## 📁 Project Structure

```
df_defence/
├── manage.py                 # Django management script
├── db.sqlite3               # SQLite database
├── requirements.txt         # Python dependencies
├── dl_ids/                  # Django project settings
│   ├── settings.py         # Main configuration
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI configuration
├── main/                    # Main application
│   ├── models.py           # Database models
│   ├── views.py            # Web views
│   ├── ddos_middleware.py  # DDoS detection middleware
│   ├── DL/                 # Deep learning modules
│   └── monitorTraffic/     # Traffic monitoring
├── model/                   # Pre-trained models
│   ├── best_model_cnn.pth
│   ├── best_model_lstm.pth
│   └── best_model_cnn_lstm_attention.pth
├── templates/               # HTML templates
├── static/                  # Static files (CSS, JS)
└── test_environment/        # Testing tools
    ├── run_test.py         # Main test runner
    ├── attack_simulator.py # Attack simulation
    ├── traffic_generator.py # Traffic generation
    └── analyze_results.py  # Result analysis
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a virtual environment
3. Install development dependencies
4. Run tests before submitting changes

### Adding New Attack Types
1. Extend `attack_simulator.py`
2. Update detection logic in `ddos_middleware.py`
3. Add corresponding model training data
4. Update documentation

## 📄 License

This project is for educational and research purposes. Please ensure compliance with local laws and regulations when using attack simulation features.

## 📞 Support

For technical support or questions:
- Check the troubleshooting section above
- Review Django logs for error details
- Ensure all dependencies are properly installed
- Verify network connectivity and permissions
