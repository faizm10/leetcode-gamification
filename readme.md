# 🚆 TransitFlow

**TransitFlow** is a backend API built with **FastAPI** that reads **GO Transit GTFS files** (CSV format) and provides clean, developer-friendly endpoints for:

* Listing and searching **routes**
* Listing and searching **stops**
* Predicting **crowd levels** (prototype model for now)

For now, all data is **read directly from CSV files** so it’s quick and easy to test without setting up a database.

---

## 🛠 Tech Stack

* **Python 3.11+**
* **FastAPI** – high-performance API framework
* **Uvicorn** – ASGI server
* **Pydantic** – data validation & serialization
* **GTFS CSV** – public transit data format (`routes.txt`, `stops.txt`, etc.)

---

## 📡 API Features

| Method | Endpoint             | Description                            |
| ------ | -------------------- | -------------------------------------- |
| GET    | `/routes`            | List/search routes                     |
| GET    | `/routes/{route_id}` | Get route details                      |
| GET    | `/stops`             | List/search stops                      |
| GET    | `/stops/{stop_id}`   | Get stop details                       |
| GET    | `/predict`           | Predict crowd level for a route & stop |

---

## 🧠 Crowd Prediction Idea

Right now, the **predict** endpoint uses a placeholder.
The goal is to replace it with a trained model that considers:

1. **Historical ridership patterns** from CSV/GTFS + public reports
2. **Time-based trends** – weekday rush hours, weekend lows
3. **Stop-specific patterns** – since some stops are always busier (based on real rider experience)
4. **Special events & anomalies** – game days, holidays, weather

Example model approach:

* Start with **rule-based logic** (e.g., “If weekday 7–9 AM and stop in downtown core → high crowd”)
* Transition to a **machine learning model** once enough data is collected
* Use personal ride knowledge as seed training data to bootstrap predictions before large-scale datasets are integrated

