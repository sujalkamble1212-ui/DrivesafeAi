# 🚗 DriveSafe AI — Real-Time Driver Drowsiness & Distraction Detection System

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask Framework](https://img.shields.io/badge/Flask-3.0.2-green.svg)](https://flask.palletsprojects.com/)
[![React Version](https://img.shields.io/badge/React-19.0-61dafb.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8.1.1-646cff.svg)](https://vitejs.dev/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15%2B-FF6F00.svg)](https://www.tensorflow.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.9.0-red.svg)](https://opencv.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-blueviolet.svg)](https://docs.ultralytics.com/)
[![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](LICENSE)

**DriveSafe AI** is an advanced, real-time computer vision and deep learning system engineered to prevent vehicle accidents caused by driver fatigue, inattention, and distraction. By analyzing live webcam video streams, DriveSafe AI monitors eye states, head orientation, yawning patterns, and mobile phone usage to instantly trigger visual and voice warnings while tracking session safety metrics.

---

## 🌟 Key Features

- 👁️ **Eye Closure & Drowsiness Detection**: Uses a custom-trained Convolutional Neural Network (CNN) in Keras/TensorFlow to analyze eye aspect regions. Detects micro-sleeps (>2.5s eye closure) while filtering out natural blinks.
- 🗣️ **Yawn Frequency Analysis**: Computes Mouth Aspect Ratio (MAR) using MediaPipe 468-point 3D Face Landmarks to identify driver tiredness.
- 🔄 **Head Pose & Inattention Tracking**: Calculates 3D head rotation (Yaw & Pitch angles) via OpenCV `SolvePnP` to detect when a driver looks away from the road (>1.5s).
- 📱 **Cell Phone Distraction Detection**: Integrated Ultralytics YOLOv8 object detection model identifies mobile phone usage in real-time (>1.0s exposure).
- 🚨 **Multi-Modal Alert Engine**:
  - Real-time dynamic audio alarm trigger.
  - Text-to-Speech (TTS) voice warnings ("*Warning! Driver drowsiness detected!*").
  - Automated snapshot capture of rule violations for audit reports.
- 📈 **Interactive Live Dashboard & Analytics**:
  - Real-time Driver Safety Score calculation (0–100%).
  - Live webcam canvas with computer vision overlays.
  - Charts showing eye aspect ratio trend lines, yawn counts, and distraction frequencies over time.
- 📄 **PDF Report Generation**: Automated generation of comprehensive trip safety PDF reports using ReportLab with session metrics, violation chronologies, and screenshots.
- ⚙️ **Configurable AI Sensitivity**: Adjustable thresholds (Low, Medium, High) for eye closure time, head tilt sensitivity, and alert frequencies.
- 🔐 **Secure Authentication & Management**: JWT-backed authentication, encrypted user credentials with bcrypt, and session history management.

---

## 🏗️ System Architecture

```
                                  +-----------------------+
                                  |   Webcam Video Stream |
                                  +-----------+-----------+
                                              |
                                              v
                              +---------------+---------------+
                              |    React + Vite Frontend      |
                              |   (Real-time Canvas / WebSockets)|
                              +---------------+---------------+
                                              | (Base64 Frames / REST API)
                                              v
                              +---------------+---------------+
                              |     Flask AI Backend Server   |
                              +---------------+---------------+
                                              |
      +-------------------+-------------------+-------------------+-------------------+
      |                   |                   |                   |                   |
      v                   v                   v                   v                   v
+-----+-----+       +-----+-----+       +-----+-----+       +-----+-----+       +-----+-----+
|  CNN Eye  |       | MediaPipe |       | MediaPipe |       |  YOLOv8   |       |   Alert   |
| Drowsiness|       | Head Pose |       | Yawn (MAR)|       |  Phone   |       |  Manager  |
|  Detector |       | (SolvePnP)|       |  Detector |       |  Detector |       |   Engine  |
+-----------+       +-----------+       +-----------+       +-----------+       +-----------+
```

---

## 🛠️ Technology Stack

### **Backend & AI Pipeline**
- **Language**: Python 3.10+
- **Framework**: Flask, Flask-RESTful, Flask-CORS, Flask-JWT-Extended
- **Deep Learning / CV**: TensorFlow / Keras (CNN Eye Classifier), OpenCV, MediaPipe (Face Mesh), Ultralytics YOLOv8
- **Database**: SQLite (SQLAlchemy ORM) — Auto-initialized on startup
- **Reporting**: ReportLab (PDF Engine)

### **Frontend & User Interface**
- **Framework**: React 19, Vite
- **Styling**: Tailwind CSS, Lucide React (Icons), Framer Motion (Animations)
- **Data Visualization**: Chart.js, React-ChartJS-2
- **State & Routing**: React Router DOM v7, Context API

---

## 📂 Project Structure

```
DriveSafeAI/
├── backend/
│   ├── app.py                      # Flask Application Entry Point & AI initialization
│   ├── config.py                   # Central Config & AI Detection Thresholds
│   ├── extensions.py               # Database & JWT Extensions
│   ├── .env.example                # Environment configuration template
│   ├── best_eye_model.keras        # Pre-trained Keras CNN model for Eye State Detection
│   ├── labels.txt                  # Model labels (Closed, Open)
│   ├── yolov8n.pt                  # YOLOv8 nano model for cell phone detection
│   ├── detection/                  # Core Computer Vision Engine
│   │   ├── eye_detection.py        # Keras CNN eye processing
│   │   ├── head_pose.py            # 3D Head pose estimation using MediaPipe
│   │   ├── yawn_detection.py       # Mouth Aspect Ratio (MAR) computation
│   │   ├── phone_detection.py      # YOLOv8 phone detection module
│   │   ├── alert_manager.py        # Warning triggers & screenshot manager
│   │   └── report_generator.py     # ReportLab PDF generator
│   └── routes/                     # REST API Endpoints
│       ├── auth.py                 # Login / Register / Profile management
│       ├── monitoring.py           # Real-time frame processing endpoint
│       ├── sessions.py             # Session start/stop/history handling
│       ├── alerts.py               # Alert history & screenshot fetching
│       ├── reports.py              # PDF trip report generation & download
│       └── settings.py             # User detection sensitivity configuration
├── frontend/
│   ├── index.html                  # HTML entry point
│   ├── vite.config.js              # Vite configuration & dev proxy settings
│   ├── package.json                # React dependencies & scripts
│   └── src/
│       ├── App.jsx                 # Navigation & Route layout
│       ├── main.jsx                # Application root rendering
│       ├── components/             # Reusable UI components (Navbar, Alert, Canvas)
│       ├── context/                # AuthContext & MonitoringContext
│       ├── hooks/                  # Custom hooks (useWebcam, useAlertSound)
│       ├── pages/                  # Page Views
│       │   ├── Dashboard.jsx       # Live monitoring & AI overlay dashboard
│       │   ├── History.jsx         # Past trip session logs
│       │   ├── Login.jsx           # User authentication
│       │   ├── Profile.jsx         # Driver profile overview
│       │   ├── Register.jsx        # New user registration
│       │   ├── Reports.jsx         # PDF generation & trip statistics viewer
│       │   └── Settings.jsx        # Thresholds & sensitivity customization
│       └── services/               # Axios API clients
└── README.md                       # Main Project Documentation
```

---

## 🚀 Quick Start Guide

### Prerequisites
Make sure you have the following software installed:
- **Python**: `3.10` or higher
- **Node.js**: `v18.0.0` or higher
- **npm**: `v9.0.0` or higher
- A working **Webcam**

---

### 1. Setting Up the Backend

1. Navigate to the `DriveSafeAI/backend` directory:
   ```bash
   cd DriveSafeAI/backend
   ```

2. Create and activate a virtual environment:
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   Copy `.env.example` to `.env`:
   ```bash
   # On Windows PowerShell
   Copy-Item .env.example .env

   # On macOS/Linux
   cp .env.example .env
   ```

5. Start the Flask Backend Server:
   ```bash
   python app.py
   ```
   The backend API will start running at `http://localhost:5000`. The SQLite database will automatically initialize on first launch.

---

### 2. Setting Up the Frontend

1. Navigate to the `DriveSafeAI/frontend` directory:
   ```bash
   cd DriveSafeAI/frontend
   ```

2. Install Node.js package dependencies:
   ```bash
   npm install
   ```

3. Start the Vite development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5173
   ```

---

## 🤖 Pre-Trained Models Included

The repository includes pre-trained model weights ready for immediate use:
- **`best_eye_model.keras`**: Pre-trained Keras CNN model for real-time eye state classification (Open vs Closed).
- **`yolov8n.pt`**: Pre-trained Ultralytics YOLOv8 object detection model configured for mobile phone detection.

---

## ⚙️ AI Detection Parameters & Thresholds

Default detection thresholds configured in `config.py`:

| Parameter | Default Value | Description |
|---|---|---|
| `EYE_CLOSED_THRESHOLD` | `0.45` | Keras model probability threshold below which an eye is classified as closed. |
| `DROWSINESS_SECONDS` | `2.5s` | Duration of continuous eye closure before triggering a Drowsiness Alert. |
| `HEAD_YAW_THRESHOLD` | `35°` | Angle limit for head turning left or right. |
| `HEAD_PITCH_THRESHOLD` | `30°` | Angle limit for head tilting up or down. |
| `HEAD_DISTRACTION_SECONDS` | `1.5s` | Time looking away from road before triggering Distraction Alert. |
| `MAR_THRESHOLD` | `0.6` | Mouth Aspect Ratio cutoff for yawn detection. |
| `PHONE_CONFIDENCE` | `0.35` | Minimum YOLOv8 confidence score for detecting cell phones. |
| `PHONE_ALERT_SECONDS` | `1.0s` | Continuous phone holding duration before triggering Distraction Alert. |

---

## 📊 REST API Endpoints Overview

### **Authentication (`/api/auth`)**
- `POST /api/auth/register` — Register a new driver account.
- `POST /api/auth/login` — Authenticate and return JWT access token.
- `GET /api/auth/profile` — Fetch driver profile and metrics.

### **Live Monitoring (`/api/monitor`)**
- `POST /api/monitor/process_frame` — Accepts a webcam frame (Base64 JPEG), runs AI detection models, and returns real-time detection statuses, bounding boxes, and alert flags.

### **Session Management (`/api/sessions`)**
- `POST /api/sessions/start` — Start a new driver trip monitoring session.
- `POST /api/sessions/stop` — End current session and summarize safety score.
- `GET /api/sessions/history` — Get historic list of driver trips.

### **Alerts & Reports (`/api/alerts` & `/api/reports`)**
- `GET /api/alerts/session/<session_id>` — Fetch logged violation alerts with timestamps and screenshot URLs.
- `GET /api/reports/download/<session_id>` — Generate and download a PDF summary report.

### **Settings (`/api/settings`)**
- `GET /api/settings` — Get current user sensitivity preferences.
- `PUT /api/settings` — Update sensitivity multipliers (Low, Medium, High).

---

## 🐳 Docker Deployment

To build and run locally with Docker:
```bash
cd DriveSafeAI/backend
docker build -t drivesafe-backend .
docker run -p 5000:5000 drivesafe-backend
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.

---

## 🤝 Acknowledgments

- **MediaPipe**: For high-fidelity face mesh landmark detection.
- **Ultralytics YOLOv8**: For object detection capabilities.
- **TensorFlow & Keras**: For deep neural network execution.
