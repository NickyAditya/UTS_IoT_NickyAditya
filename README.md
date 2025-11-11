# 🌟 UTS IoT - Nicky Aditya

[![IoT](https://img.shields.io/badge/IoT-Project-blue.svg)](https://github.com/NickyAditya/UTS_IoT_NickyAditya)
[![Flask](https://img.shields.io/badge/Flask-Web%20Framework-green.svg)](https://flask.palletsprojects.com/)
[![MQTT](https://img.shields.io/badge/MQTT-Protocol-orange.svg)](https://mqtt.org/)
[![Wokwi](https://img.shields.io/badge/Wokwi-Simulator-purple.svg)](https://wokwi.com/)

## 📋 Deskripsi Project

Project IoT yang mengimplementasikan sistem monitoring dan kontrol real-time menggunakan berbagai teknologi modern. System ini menampilkan data live streaming dengan antarmuka web yang interaktif dan responsif.

## 🚀 Fitur Utama

- 📊 **Live Data Streaming** - Monitoring data sensor secara real-time
- 🌐 **Web Interface** - Frontend yang user-friendly dan responsive
- 🔄 **MQTT Integration** - Protokol komunikasi yang efisien
- 🖥️ **Flask Backend** - Server yang robust dan scalable
- 📱 **Cross-platform** - Dapat diakses dari berbagai perangkat
- 🔧 **Wokwi Simulation** - Testing dan development menggunakan simulator

## 🛠️ Tech Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) | Backend Development | 3.x |
| ![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white) | Web Framework | Latest |
| ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white) | Frontend Structure | 5 |
| ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white) | Styling | 3 |
| ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black) | Frontend Logic | ES6+ |
| ![MQTT](https://img.shields.io/badge/MQTT-660066?style=flat&logo=mqtt&logoColor=white) | IoT Communication | 3.1.1 |

## 🏗️ Arsitektur System

```
┌─────────────────┐    MQTT     ┌─────────────────┐    HTTP     ┌─────────────────┐
│   Wokwi Device  │ ◄────────► │  Flask Backend  │ ◄────────► │   Web Frontend  │
│   (Simulator)   │             │     (API)       │             │    (Browser)    │
└─────────────────┘             └─────────────────┘             └─────────────────┘
        │                               │                               │
        │                               │                               │
        ▼                               ▼                               ▼
   Sensor Data                    Data Processing                 Real-time Display
   Generation                     & Storage                       & User Interface
```

## 📦 Installation & Setup

### Prerequisites
- Python 3.11.5
- pip (Python package manager)
- Git

### Quick Start

1. **Clone Repository**
   ```bash
   git clone https://github.com/NickyAditya/UTS_IoT_NickyAditya.git
   cd UTS_IoT_NickyAditya
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env file with your configurations
   ```

4. **Run Application**
   ```bash
   python app_mqtt.py
   ```

5. **Access Application**
   - Open browser: `http://localhost:5000`
   - Wokwi Simulator: [Link to your Wokwi project]

## 🎯 Usage

### Web Interface
1. Buka browser dan akses `http://localhost:5000`
2. Monitor data sensor real-time pada dashboard
3. Gunakan kontrol panel untuk mengatur parameter
4. View historical data dan analytics

### MQTT Communication
- **Broker**: `broker.hivemq.com` (atau sesuai konfigurasi)
- **Topic Subscribe**: `iot/sensor/data`
- **Topic Publish**: `iot/control/commands`
- **Port**: 1883

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/data` | Mendapatkan data sensor terbaru |
| POST | `/api/control` | Mengirim perintah kontrol |
| GET | `/api/history` | Mendapatkan data historis |
| WebSocket | `/ws` | Real-time data streaming |

## 🔧 Configuration

Edit file `config.py` untuk mengubah pengaturan:

```python
# MQTT Settings
MQTT_BROKER = "your-broker-url"
MQTT_PORT = 1883
MQTT_TOPIC = "iot/data"

# Flask Settings
DEBUG = True
PORT = 5000
```

## 📈 Monitoring Dashboard

Dashboard menampilkan:
- 📊 Real-time charts dan graphs
- 🌡️ Temperature & humidity readings
- 💡 Device status indicators
- 📱 Mobile-responsive design
- 🔄 Auto-refresh functionality

## 📁 Project Structure

```
UTS_IoT_NickyAditya/
├── 📂 static/
│   ├── 📄 sytle.css
│   ├── 📄 index.js
├── 📂 templates/
│   ├── 📄 index.html
├── 📄 app_mqtt.py
```

## 👨‍💻 Author

**Nicky Aditya**
- GitHub: [@NickyAditya](https://github.com/NickyAditya)
- Email: [nicky.aditya@mhs.itenas.ac]

## 🙏 Acknowledgments

- Flask community untuk web framework yang excellent
- Wokwi untuk platform simulasi IoT yang amazing
- MQTT.org untuk protokol komunikasi yang reliable
- Semua contributor yang telah membantu project ini

---

⭐ **Jangan lupa untuk memberikan star jika project ini membantu!** ⭐

---

<div align="center">
  <img src="https://komarev.com/ghpvc/?username=NickyAditya&repo=UTS_IoT_NickyAditya&color=blue" alt="Profile views">
</div>
