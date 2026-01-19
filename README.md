# 🧹Smart Data Steward Agent

**An Autonomous Data Cleaning & Analysis Agent built with LangChain, Gemini, and Streamlit.**

## 🚀 The Problem
Data Scientists spend **80% of their time cleaning data**. Manual cleaning is error-prone, slow, and lacks auditability.

## 💡 The Solution
The **Smart Data Steward** is an "Human-in-the-Loop" AI Agent that:
1.  **Diagnoses** data quality issues (missing values, outliers, type mismatches).
2.  **Proposes & Executes** cleaning code autonomously using Python REPL.
3.  **Visualizes** insights on-the-fly.
4.  **Audits** every change for compliance.

## 🛠️ Tech Stack
* **Orchestration:** LangChain (Pandas DataFrame Agent)
* **LLM:** Google Gemini 1.5 Flash
* **Frontend:** Streamlit (Custom Session State Management)
* **Data Processing:** Pandas, Regular Expressions (Regex)
* **Visualization:** Matplotlib

## 🌟 Key Features
* **Auto-Repair:** intelligently fixes currency symbols (e.g., `₹20,000` -> `20000.0`), text-mixed numbers, and missing values.
* **Safe Execution:** Uses a sandbox environment with `errors='coerce'` strategies to prevent crashes.
* **Visualization Engine:** Generates histograms and scatter plots from natural language prompts.
* **Audit Trail:** Exports a full log of all transformations for data governance.

## 💻 How to Run Locally
1.  Clone the repo.
2.  Install dependencies: `pip install -r requirements.txt`
3.  Set up `.env` with `GOOGLE_API_KEY`.
4.  Run: `streamlit run app.py`
