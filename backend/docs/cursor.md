# **TransitFlow – GO Transit Crowd Predictor**

## 📌 What is this?

TransitFlow is a backend project that predicts how busy a GO Transit train or bus will be at a specific stop and time.
It uses:

* Past schedule and fare data from `/files`
* A PostgreSQL database
* A small machine learning model (scikit-learn)
* An API (FastAPI) for making predictions

---

## 📂 Data in `/files`

These files come from GO Transit’s GTFS feed and will be loaded into the database.

| File                     | What it contains                                  | How we’ll use it                                           |
| ------------------------ | ------------------------------------------------- | ---------------------------------------------------------- |
| **routes.txt**           | All GO Transit routes (IDs, names, colors, types) | Fill the `routes` table                                    |
| **stops.txt**            | All stops/stations with coordinates and zone IDs  | Fill the `stops` table                                     |
| **stop\_amentities.txt** | Shelter, washroom, bike rack, bench availability  | Join to `stops` for extra features                         |
| **fare\_attributes.txt** | Fare prices, currency, and transfer rules         | Optional — could be used for cost features                 |
| **fare\_rules.txt**      | Links fares to origin/destination zones           | Optional — can join to predict based on trip distance/cost |
| **transfers.txt**        | Allowed transfers between stops                   | Optional — could be used for trip chaining                 |
| **feed\_info.txt**       | Feed publisher, date range, version               | Metadata only                                              |
| **trips.txt**       | Has all the trips               | fill the `trips`
---

## 🎯 What the backend will do

1. **Load this data** into Postgres with SQLAlchemy models
2. **Add “observations” table** for boarding/alighting counts (can be simulated first)
3. Build a **baseline predictor** (historical averages)
4. Train an **ML model** to improve accuracy
5. Cache predictions in Redis
6. Expose **API endpoints**:

   * `/trips` → list routes
   * `/trips/{id}/stops` → list stops
   * `/predict` → crowd prediction
   * `/observations` (admin) → add new data
   * `/train` (admin) → retrain model

---

## ⚙️ How predictions will work

1. **Check cache (Redis)** for a stored prediction
2. If not found:

   * Query DB for historical data
   * Build features (time, day, weather, stop amenities, fare zone)
   * Run the model to get a crowd level (light, moderate, packed)
3. Save result in cache for quick future lookups

---

## 🚀 Running locally

```bash
docker compose up --build
```

API docs:

```
http://localhost:8000/docs
```

Run tests:

```bash
pytest
```