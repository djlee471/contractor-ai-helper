# Home Repair Helper (AI-Powered Customer Assistant)

This app helps homeowners:
- Explain insurance estimates in plain English.
- Understand a typical order of home repair tasks.
- Get interior design suggestions (tile, carpet, wall color).
- All results are available in **English (primary)** and **Spanish (courtesy translation)**.

The app is designed to:
- Avoid substituting for professional insurance, legal, or construction advice.
- Help customers ask better questions to their adjuster and contractor.
- Avoid contradicting official estimates or contractor instructions.
- Never store user data.

---

## Running Locally

### 1. Install dependencies

### 2. Create a `.env` file
(You may base it on `.env.example`)

### 3. Run the app

Your browser will open automatically at `http://localhost:8501`.

---

## Deployment on Streamlit Cloud

### 1. Add your OpenAI API key in Streamlit Secrets  
Go to:

Add:

(Do *not* commit your `.env` file to GitHub.)

### 2. Deploy the app  
Point Streamlit Cloud to your GitHub repository.  
Streamlit will automatically install dependencies from `requirements.txt`.

No `.env` file is required on Streamlit Cloud.

---

## Project Structure
home-repair-helper/
│
├── app.py # Main Streamlit application with tab layout
├── requirements.txt # Python dependencies
├── README.md # This file
├── .gitignore # Excludes .env, logs, caches, etc.
├── .env.example # Template for local development
└── .env (not committed) # Contains your OPENAI_API_KEY locally


(Optional later: you may add `agents/` and `utils/` folders for modularization.)

---

## Notes and Disclaimers

- This tool provides **general educational information only**.
- It does **not** provide legal, insurance, engineering, or contractor advice.
- The **insurance company**, **policy documents**, and **your contractor’s written plan**
  are always the final authority.
- The Spanish output is a **courtesy translation**; English is the primary reference.
- The app does not save data; all processing happens in-session only.

---

## Features Overview

### ✔ Estimate Explainer
Upload your insurance estimate (PDF or photo) and optionally your contractor’s estimate.  
The app will:
- Summarize the estimate in plain English
- Identify decisions the homeowner may need to make
- Suggest neutral follow-up questions to ask your adjuster/contractor

### ✔ Renovation Plan
Describe the damaged rooms and needed work.  
The app provides:
- A typical sequence of repairs (e.g., demo → tile → baseboards → carpet)
- A preparation checklist
- Suggested questions for the contractor

### ✔ Design Helper
Describe your wall colors, adjacent floors, and style preferences.  
The app offers:
- 2–3 design directions for tile, carpet, and grout
- Practical considerations (kids, pets, traffic)
- Suggested questions for a contractor or showroom

---

## License
This project is for educational and operational support purposes and may be adapted freely for contractor use.

