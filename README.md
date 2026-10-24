# CareerPathPredictor

An ML-based career path recommendation system — matches the technologies listed
in the project synopsis:

- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Python (Flask)
- **Machine Learning:** scikit-learn (Random Forest classifier), Pandas, NumPy
- **Database:** SQLite (lightweight, zero-setup — swap for MySQL later if needed)
- **Authentication:** JWT (JSON Web Tokens)

This is a real, working full-stack project (not a mockup). It has a trained
ML model, a live database, working login/signup, and a feedback loop —
exactly as described in the synopsis.

---

## What it does

1. You enter your skills and interests on the website.
2. A trained Random Forest model (trained on a generated career-skill
   dataset) predicts your top 5 best-fit careers, each with a match %.
3. For each career, it shows which skills you already have and which
   ones you're missing (skill-gap analysis).
4. It suggests free resources to close those gaps.
5. You can mark a suggestion as "relevant" or "irrelevant" — this is
   saved to the database (the feedback loop from the synopsis).

---

## Project structure

```
CareerPathPredictor/
├── backend/
│   ├── app.py                 # Flask server — all API routes
│   ├── database.py            # SQLite database functions
│   ├── train_model.py         # Trains the ML model
│   ├── requirements.txt       # Python packages needed
│   ├── data/
│   │   ├── career_skill_map.py    # Career-skill knowledge base
│   │   └── generate_dataset.py    # Creates the training dataset
│   └── models/                # Trained model gets saved here
└── frontend/
    ├── index.html              # Main page
    ├── style.css                # Styling
    └── app.js                   # Talks to the backend API
```

---

## How to run it (step-by-step)

You need **Python 3.9 or newer** installed on your laptop.
(Check by opening Command Prompt / Terminal and typing `python3 --version`)

### Step 1 — Open a terminal in the `backend` folder

Windows: open Command Prompt, then:
```
cd path\to\CareerPathPredictor\backend
```
Mac/Linux:
```
cd path/to/CareerPathPredictor/backend
```

### Step 2 — Install the required Python packages

```
pip install -r requirements.txt
```

If that gives an error, try:
```
pip3 install -r requirements.txt
```

### Step 3 — Generate the training data and train the ML model

```
python train_model.py
```

This will automatically generate the dataset (`data/career_dataset.csv`)
and train the Random Forest model, then save it in `backend/models/`.
You should see something like:
```
Model trained. Test accuracy: 89.93%
Model saved -> .../models/career_model.pkl
```

### Step 4 — Start the backend server

```
python3 app.py
```

Leave this terminal window open — it's your live server. You should see:
```
Running on http://127.0.0.1:5000
```

### Step 5 — Open the website

Open a **new** terminal window (keep the backend one running), go to the
`frontend` folder, and run:

```
cd path/to/CareerPathPredictor/frontend
python3 -m http.server 8080
```

Now open your browser and go to:
```
http://127.0.0.1:8080
```

That's it — the website is live and fully connected to your ML backend!

---

## For your project demo / viva

Things you can show/explain:

- **The dataset problem (synopsis challenge):** Since ready-made career-skill
  datasets don't exist publicly, `generate_dataset.py` builds a synthetic
  training dataset by simulating hundreds of student profiles for each
  career (with realistic noise — missing skills, extra unrelated skills).
- **The ML model:** `train_model.py` trains a `RandomForestClassifier` from
  scikit-learn on this dataset — a real classification model, not a fake
  lookup table.
- **Confidence scores:** The backend calls `model.predict_proba()` to get
  a genuine probability for each career, then blends it with interest
  overlap for the final match %.
- **Skill-gap analysis:** For each predicted career, the backend compares
  your selected skills against that career's required skill list.
- **Auth:** Signup/Login use `werkzeug` password hashing (passwords are
  never stored in plain text) and JWT tokens for sessions.
- **Feedback loop:** Every 👍/👎 click is saved to the `feedback` table in
  the database — in a bigger version, this data could be used to retrain
  and improve the model over time.

---

## Notes

- The database file (`backend/careerpath.db`) is created automatically the
  first time you run `app.py` — you don't need to set anything up manually.
- If you want to reset all data (users, predictions, feedback), just delete
  `backend/careerpath.db` and restart the server — a fresh one will be made.
- To add more careers, just edit `backend/data/career_skill_map.py`, then
  re-run `python3 train_model.py` to retrain the model on the new data.

### Input rules (checked by the backend)

- Sign up needs a name, a valid e-mail address and a password of at least 6 characters.
- To get a prediction, select **at least one skill** (the model predicts from skills; interests are optional and
  only adjust the match %). Unknown skill names are ignored.
- Feedback (👍/👎) is saved once per result card; clicking again only changes the earlier vote.
- If the server sends an error, the page shows a message instead of crashing.

### About the accuracy number (for the viva)

The 89.93% test accuracy is measured on the **synthetic** dataset that `generate_dataset.py` builds from the same
career-skill list, so it shows that the model learned that list, not how well it predicts real students. Careers with
very similar skills (for example Data Scientist and AI/ML Engineer) are the ones the model mixes up most.
The model file in `backend/models/` was trained with the exact library versions in `requirements.txt`
(scikit-learn 1.5.1). If you change the versions, run `python3 train_model.py` again.
