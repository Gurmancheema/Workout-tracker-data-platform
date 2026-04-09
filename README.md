# 🏋️ Workout Tracker Data Platform

A **production-grade, full-stack data application** designed with a strong focus on **data engineering principles**. This project goes beyond a traditional CRUD app by treating workout tracking as a **data modeling, processing, and analytics problem**.

---

## 🚀 Project Vision

Most fitness applications focus only on logging workouts. This platform is built to:

- Model workout data using **relational design best practices**
- Ensure **data integrity and consistency** across entities
- Enable **efficient querying for analytics and insights**
- Serve as a foundation for **scalable data pipelines and ML systems**

This is not just a tracker — it's a **mini data platform for fitness data**.

---

## 🧠 Key Highlights

- 🔄 End-to-end architecture: UI → Backend → Database → Cloud
- 🗄️ Strong relational schema with normalized design
- ☁️ Cloud-native backend using Supabase (PostgreSQL)
- ⚡ Interactive frontend powered by Streamlit
- 🧩 Modular and extensible codebase
- 🧪 Real-world debugging & edge case handling

---

## 🏗️ Architecture Overview

```
            ┌──────────────────────┐
            │   Streamlit Frontend │
            └─────────┬────────────┘
                      │
                      ▼
            ┌──────────────────────┐
            │  Python Backend Layer│
            │ (Business Logic / DB)│
            └─────────┬────────────┘
                      │
                      ▼
            ┌──────────────────────┐
            │ PostgreSQL (Supabase)│
            │  Managed Cloud DB    │
            └─────────┬────────────┘
                      │
                      ▼
            ┌──────────────────────┐
            │  Cloud Deployment    │
            │ (Streamlit Cloud)    │
            └──────────────────────┘
```

---

## 🗃️ Data Modeling (Core Strength)

### Entities
- **Users**
- **Workout Sessions**
- **Exercises**
- **Exercise Sets (`exercises_sets`)**

### Design Decisions

- Fully **normalized schema (3NF)** to eliminate redundancy
- **Foreign key constraints** for referential integrity
- Optimized for **analytical queries (session-based tracking)**
- Designed for **future extensibility** (multi-user, analytics, ML)

---

## ⚙️ Features

### ✅ Workout Session Management
- Create sessions per user per date
- Duplicate session prevention via backend validation

### 💪 Exercise Mapping
- Exercises mapped to muscle groups
- Dynamic dropdowns powered by backend queries

### 📊 Set Tracking
- Track reps, weight, and sets
- Structured storage enabling downstream analytics

### 🔁 State Management
- Robust Streamlit session state handling
- Form reset and validation logic

### ☁️ Cloud Persistence
- Fully integrated with Supabase PostgreSQL
- Data persists independently of UI sessions

---

## 🛠️ Tech Stack

| Layer | Technology |
|------|-----------|
| Frontend | Streamlit |
| Backend | Python |
| Database | PostgreSQL (Supabase) |
| Deployment | Streamlit Cloud |
| Version Control | Git & GitHub |

---

## 🔍 Engineering Challenges & Solutions

### 1. Handling NULL Results from Queries
- Prevented `NoneType` crashes using defensive checks
- Implemented safe fetch patterns for SQL queries

### 2. Session State Management in Streamlit
- Built controlled reset mechanisms
- Avoided stale UI states using explicit state keys

### 3. Timezone Inconsistencies
- Identified cloud vs local time mismatch
- Standardized handling for consistent timestamps

### 4. Data Mapping Issues
- Debugged missing muscle group mappings
- Ensured completeness in lookup tables

### 5. Dependency Optimization
- Cleaned unnecessary packages from `requirements.txt`
- Reduced deployment overhead

---

## 📈 Future Roadmap

- 📊 Analytical dashboards (progress tracking, KPIs)
- 🤖 ML-based workout recommendations
- 🔐 Authentication & multi-user support
- 🌐 REST API layer (FastAPI)
- ⚛️ Migration to React frontend
- 🔄 Data pipelines (Airflow / Spark integration)

---

## 💡 Why This Project Stands Out

This project demonstrates:

- Real-world **data engineering thinking**
- Strong **data modeling fundamentals**
- Hands-on **cloud deployment experience**
- Ability to **debug production-like issues**
- Building **scalable systems, not just scripts**

---

## 🧑‍💻 Getting Started

### 1. Clone the Repository
```bash
git clone <your-repo-link>
cd workout-tracker-data-platform
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file and add:

```
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
```

### 4. Run the Application
```bash
streamlit run app/main.py
```

---

## 🌐 Live Demo

> [https://personal--workout-tracker.streamlit.app/]

---

## 🏷️ GitHub Topics (for better reach)

Add these tags to your repository:

```
data-engineering
postgresql
streamlit
supabase
python
etl
data-platform
analytics
cloud
```

---

## 🤝 Contributing

Contributions are welcome!

- Fork the repo
- Create a feature branch
- Submit a pull request

---

## 📬 Final Note

This project reflects an **end-to-end data engineering journey** — from schema design to cloud deployment.

If you're a recruiter or engineer reviewing this repo:

> This project showcases my ability to **design, build, and deploy scalable data systems with production-level thinking.**

---

⭐ If you found this useful, consider starring the repository!

