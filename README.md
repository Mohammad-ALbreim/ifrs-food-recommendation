# IFRS — Intelligent Food Recommendation System

A graduation project that recommends restaurant meals to customers based on their nutrition profile, goals, and mood — combining a Django web app, an R-based mood classifier, and a Retrieval-Augmented Generation (RAG) pipeline built on OpenAI embeddings and FAISS.

## Overview

IFRS has two portals:

- **Restaurant portal** — restaurants sign in, manage a profile, and run full CRUD on their menu (meals with price, calories, macros, allergens, and an image).
- **Customer portal** — customers sign up with a nutrition profile (age, weight, height, goal, likes/dislikes, allergies, calorie range), browse restaurants and meals, and take a short mood quiz to get personalized meal recommendations with an AI-generated explanation.

## How it works

1. **Quiz → Mood analysis.** The customer answers 7 quiz questions. Django passes the answers as JSON to an R script (`mood_analysis.R`) via `subprocess`, which returns a mood label (e.g. *Excited*, *Neutral*, *Tired*).
2. **Filtering & scoring.** Meals are filtered by the customer's calorie range, allergies, and likes/dislikes, then scored with a goal-aware heuristic (`loss`, `gain`, `maintain` favor different calorie/protein/fat trade-offs). The top 6 meals are kept.
3. **RAG explanation.** The customer profile, mood, and recommended meals are turned into a context block. `rag_query.py` embeds the query with OpenAI (`text-embedding-3-small`), retrieves the closest documents from a FAISS index built from the restaurant/meal/customer data, and asks `gpt-4o-mini` to explain why the meals fit.
4. **Nutrition chat.** A follow-up chat endpoint (`/nutrition/chat/`) reuses the last recommendation context so customers can ask follow-up questions about their results.

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Django 4/5 |
| Database | MySQL |
| Mood analysis | R (`jsonlite`), invoked as a subprocess |
| Embeddings / RAG | OpenAI API, FAISS (`faiss-cpu`), NumPy |
| Media | Pillow (meal images) |

## Project structure

```
ifrs_project/
├── core/                   # Django app: models, views, forms, urls, migrations
├── ifrs_project/            # Django project settings, root urls, WSGI/ASGI
├── templates/                # HTML templates (customer/, restaurant/, admin/)
├── static/                   # Static assets per portal
├── media/meals/               # Uploaded meal images
├── mood_analysis.R            # Mood classifier used by the quiz flow
├── r_scripts/predict_mood.R    # Alternate/standalone mood predictor
├── rag_builder.py              # Builds the FAISS index + dataset from live Django data
├── rag_query.py                 # RAG search + chat answer generation
├── inspect_pkl.py                # Utility to inspect a pickled embeddings file
└── requirements.txt
```

## Setup

### Prerequisites

- Python 3.10+
- MySQL Server
- An OpenAI API key — needed for the RAG explanations and chat

### 1. Clone and create a virtual environment

```bash
git clone https://github.com/Mo7ammadosama/IFRS_Project.git
cd IFRS_Project
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Configure the database

Create a MySQL database and update `ifrs_project/settings.py` → `DATABASES` with your host/port/user/password (defaults expect a local MySQL instance on port `3308`, database `intelligent_food_recommendation`).

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 3. Configure the OpenAI key

```bash
set OPENAI_API_KEY=your-key-here     # Windows (cmd)
$env:OPENAI_API_KEY="your-key-here"  # Windows (PowerShell)
export OPENAI_API_KEY=your-key-here  # macOS/Linux
```

### 4. Run the app

```bash
python manage.py runserver
```

### 5. Build the RAG index

With the server running (so `rag_builder.py` can pull data from `/rag/export/`):

```bash
python rag_builder.py
```

This regenerates `rag_index.faiss` and `rag_dataset.json` from the current restaurants/meals/customers in the database. Re-run it whenever the menu data changes.

## Key routes

| Route | Description |
|---|---|
| `/` | Welcome page |
| `/restaurant/login/` | Restaurant sign-in |
| `/restaurant/dashboard/` | Restaurant dashboard |
| `/restaurant/meals/` | Meal CRUD list |
| `/customer/signup/`, `/customer/login/` | Customer auth |
| `/customer/quiz/` | Mood quiz |
| `/customer/quiz/result/` | Scored recommendations + AI explanation |
| `/nutrition/chat/` | Follow-up chat about the last recommendation |
| `/rag/export/` | JSON export of restaurants/meals/customers, used by `rag_builder.py` |

## Notes for future work

This is an academic prototype — a few things are intentionally simplified and worth hardening before any real deployment:

- Passwords are stored in plain text (`Customer.password`, `Restaurant.password`); they should be hashed.
- `SECRET_KEY` is hardcoded and `DEBUG = True` in `settings.py`; both should move to environment variables for production.
- The R executable path in `core/views.py` is hardcoded to a specific Windows install.

## License

Graduation project — no license specified.
