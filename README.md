# BurnoutBuddy 🌸
### A Student Wellness Tracker powered by Machine Learning

BurnoutBuddy is a desktop application that predicts your weekly burnout risk using a Random Forest ML model. Answer 8 questions about your sleep, stress, study habits, and lifestyle — and get an instant risk assessment with personalised tips and a progress chart over time.

Built for students, by a student.

---

## Features

- **ML-powered predictions** — Random Forest classifier trained on 1,000 synthetic student wellness profiles (scikit-learn)
- **Interactive Tkinter GUI** — clean multi-page interface with sliders, emoji scales, and toggle buttons
- **Personalised tips** — context-aware recommendations based on your risk level (Low / Moderate / High)
- **History tracking** — SQLite database stores your check-ins locally; matplotlib chart shows your burnout trend over time
- **Fully offline** — no accounts, no internet, no data leaves your device

---

## Demo

| Home | Weekly Check-in | Results |
|------|----------------|---------|
| Start screen with last result stats | 8-question wellness survey | Risk breakdown + personalised tips |

| History |
|---------|
| Line chart of burnout risk over time |

---

## Tech Stack

| Layer | Tools |
|-------|-------|
| GUI | Python `tkinter`, `ttk` |
| ML Model | `scikit-learn` RandomForestClassifier |
| Data | `pandas`, `numpy` (synthetic dataset — 1000 profiles) |
| Visualisation | `matplotlib` embedded via `FigureCanvasTkAgg` |
| Storage | `sqlite3` (local, no server needed) |

---

## Project Structure

```
BurnoutBuddy/
├── app.py                  # Main application entry point
├── database.py             # SQLite init, save, and fetch functions
├── setup.py                # First-time setup script
├── requirements.txt
├── data/
│   ├── generate_data.py    # Synthetic dataset generator
│   └── burnout_data.csv    # Generated training data
└── models/
    ├── train_model.py      # Random Forest training script
    ├── burnout_model.pkl   # Saved trained model
    └── scaler.pkl          # StandardScaler for inference
```

---

## How It Works

1. User fills in 8 lifestyle inputs (sleep hours, study hours, stress level, exercise days, social time, breaks, water intake, screen time)
2. Inputs are scaled using a pre-fitted `StandardScaler`
3. The Random Forest model predicts one of three classes: **Low Risk**, **Moderate Risk**, or **High Risk**
4. Prediction probabilities are shown as a bar chart
5. Personalised tips are displayed based on the predicted class
6. The entry is saved to SQLite and added to the history chart

**Model accuracy: ~90%+ on held-out test set** (200 samples, stratified split)

---

## Getting Started

**Requirements:** Python 3.8+

```bash
# 1. Clone the repo
git clone https://github.com/saherkalia/burnout-buddy.git
cd burnout-buddy

# 2. Run setup (installs dependencies + trains model)
python setup.py

# 3. Launch the app
python app.py
```

Or manually:

```bash
pip install -r requirements.txt
python data/generate_data.py
python models/train_model.py
python app.py
```

---

## Input Features

| Feature | Type | Range |
|---------|------|-------|
| Sleep hours | Slider | 1–12 hrs |
| Study hours | Slider | 0–14 hrs |
| Stress level | Emoji scale | 1–10 |
| Exercise days | Slider | 0–7 days |
| Social time | Toggle | Yes / No |
| Took breaks | Toggle | Yes / No |
| Water intake | Slider | 1–15 glasses |
| Screen time (non-study) | Slider | 0–12 hrs |

---

## Why I Built This

Burnout affects a large proportion of college students globally. I wanted to build something that gives students a simple, non-judgmental weekly mirror — not a mood app, not a journaling tool, but a data-driven check-in that takes your habits seriously.

All data stays local. No tracking. Just you and your wellness journey.

---

## Future Improvements

- [ ] Web version using Streamlit or Flask
- [ ] Export history as PDF report
- [ ] Streak tracking and weekly reminders
- [ ] Model fine-tuning on real (anonymised) student data

---

## Author

**Jiya** — B.Tech CSE '27, GGSIPU Delhi  
[GitHub](https://github.com/saherkalia)
