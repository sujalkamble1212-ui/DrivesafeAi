---
title: DriveSafe AI
emoji: 🚗
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: mit
short_description: Real-time AI driver monitoring — drowsiness, distraction & phone detection
---

# 🚗 DriveSafe AI

Real-time AI-powered driver safety monitoring system.

## Features
- 👁️ **Drowsiness Detection** — TensorFlow Keras eye-state classifier
- 🤚 **Head Pose Tracking** — MediaPipe face mesh for distraction alerts
- 😮 **Yawn Detection** — Mouth Aspect Ratio via MediaPipe landmarks
- 📱 **Phone Detection** — YOLOv8 real-time object detection
- 📊 **Safety Scoring** — Live safety & attention scores per session
- 📄 **PDF Reports** — Downloadable session reports via ReportLab
- ☁️ **MongoDB Atlas** — Cloud database for users, sessions & alerts

## Environment Variables (set in Space Settings → Variables and Secrets)

| Variable | Description |
|---|---|
| `MONGODB_URI` | MongoDB Atlas connection string |
| `MONGODB_DB` | Database name (e.g. `drivesafe_ai`) |
| `SECRET_KEY` | Flask secret key |
| `JWT_SECRET_KEY` | JWT signing key |
| `CORS_ORIGINS` | Allowed origins (use `*` for HF Spaces) |

## Tech Stack
- **Frontend:** React 19 + Vite + Tailwind CSS
- **Backend:** Flask + Gunicorn + MongoEngine
- **AI Models:** TensorFlow, YOLOv8 (Ultralytics), MediaPipe
- **Database:** MongoDB Atlas
