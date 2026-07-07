# Tamil Nadu Smart Travel Planner

A premium, motion-rich full-stack Python web application designed for comprehensive travel planning, budget estimation, and itinerary generation restricted exclusively to **Tamil Nadu** destinations.

---

## 🚀 Key Features

1. **State-Restricted Selection:** Supports 14 curated Tamil Nadu regions (and Pondicherry clearly flagged as a nearby Union Territory).
2. **Premium Graphic Designer UI:** Injects custom Google Fonts (`Poppins`, `Inter`), glassmorphism layout cards, hover animations, skeleton shimmers, and looping Lottie illustrations.
3. **Smart Cost Engine (2026 baseline):** Grounded in real-world Indian domestic travel costs. Estimates hotels, food standards, and transport modes (bus, train flat-bands, metro flights, chauffeur, and self-drive cabs).
4. **Day-by-Day Itineraries:** Automatically generates customized morning, afternoon, and evening schedules scaled to the exact number of days selected.
5. **Secure Authentication:** User signup and signin backed by `bcrypt` password hashing, duplicate check validations, and a real-time visual strength meter.
6. **Trip History & CSV Export:** Displays previous plans, lets users delete, and exports selections to CSV.
7. **Plotly Analytics Dashboard:** Visualizes trip cost metrics, destination popularity, and budget allocations.
8. **Role-Gated Admin Panel:** Access to platform-wide statistics, active users list, trips deletion controls, and interactive SQLite system audit logs.

---

## 🛠️ Tech Stack

- **Frontend / Core:** [Streamlit](https://streamlit.io/) (with CSS injection & HTML layout custom components)
- **Visuals & Charts:** Plotly Express
- **Animation:** `streamlit-lottie`
- **Database & Audits:** SQLite (locally stored in `smart_travel.db`)
- **Password Security:** `bcrypt`
- **Data Export:** Pandas

---

## 📂 Project Directory Structure

```text
├── app.py                     # Entry point, session, and page routing
├── auth/                      # Authentication logic
│   └── auth.py                # BCrypt encryption, login and signup handlers
├── database/                  # Data access layer
│   ├── db.py                  # Transaction wrappers and JSON database seeding
│   └── schema.py              # SQLite table structures
├── services/                  # Business logic engines
│   ├── recommendation_engine.py # Budget and travel type filtering
│   ├── budget_engine.py       # Distance and category calculations
│   ├── itinerary_generator.py # Day-by-day activity compiler
│   └── planner.py             # Trips save and fetch orchestrator
├── pages/                     # Streamlit view modules (routed via app.py)
│   ├── dashboard.py           # Dashboard statistics and quick actions
│   ├── planner_page.py        # Interactive planner wizard
│   ├── history_page.py        # Past trips grid and CSV downloader
│   ├── analytics_page.py      # Plotly statistics charts
│   ├── admin_page.py          # Admin logs table and delete buttons
│   └── profile_page.py        # Accounts setting and password updates
├── ui/                        # Aesthetics layer
│   ├── theme.py               # Color palettes, custom fonts, CSS injection
│   ├── components.py          # Reusable top navigation, glass cards
│   └── animations.py          # Lottie animations, skeleton loader, JS count-up
├── utils/                     # Helpers
│   ├── validators.py          # Username, email, password strength calculations
│   └── logger.py              # Rotating file logs (TIMESTAMP | LEVEL | MODULE | MESSAGE)
├── data/                      # Seeding files
│   ├── destinations.json      # Tamil Nadu destinations metadata
│   └── cost_baseline.json     # Hotel, food, and transport rates baseline
├── logs/                      # Application outputs
│   └── application.log        # System execution log outputs
├── tests/                     # Unit test suites
│   ├── test_db.py             # Database and auth tests
│   └── test_engines.py        # Engine recommendation and budget calculations tests
├── requirements.txt           # Dependencies listing
└── README.md                  # Project information sheet
```

---

## ⚡ Setup & Installation

### 1. Pre-requisites
Make sure you have **Python 3.12+** installed on your system.

### 2. Install Dependencies
Install all required libraries from the terminal:
```bash
pip install -r requirements.txt
```

### 3. Execution
Launch the Streamlit server from the root of the project:
```bash
streamlit run app.py
```

### 4. Admin Access
The system initializes with a default administrator account. You can log in using:
- **Email:** `admin@smarttravel.local`
- **Password:** `Admin@123`
Use this account to inspect role-gated admin controls and review system audit logs.
