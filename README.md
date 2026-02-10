<div align="center">
  <img src="app/estimlogo.png" alt="EstimAI Logo" width="200"/>

  # 🍁 [**EstimAI**](https://estimai-british-columbia.streamlit.app/) — AI-Powered Property Price Estimator

  **Estimate any property's market value in British Columbia, Canada — powered by Machine Learning.**

  [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://estimai-british-columbia.streamlit.app/)
  ![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
  ![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-orange?logo=scikit-learn&logoColor=white)
  ![Status](https://img.shields.io/badge/Status-Live-brightgreen)

  [**🚀 Try the Live App →**](https://estimai-british-columbia.streamlit.app/)

</div>

---

## 📖 Table of Contents

- [About the Project](#-about-the-project)
- [Live Demo](#-live-demo)
- [Features](#-features)
- [How It Works](#-how-it-works)
- [Machine Learning Pipeline](#-machine-learning-pipeline)
- [Dataset](#-dataset)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation & Local Usage](#-installation--local-usage)
- [Disclaimer](#%EF%B8%8F-disclaimer)

---

## 🎯 About the Project

**EstimAI** is a full-stack Machine Learning web application that estimates residential property prices in **British Columbia, Canada**. Users simply enter an address and describe their property's characteristics — the app returns an AI-generated price estimate with a confidence range.

### Motivation

This project was built to combine two personal interests: **Artificial Intelligence** and **real estate**. The goal was to go beyond notebooks and academic exercises by building and deploying a complete, end-to-end ML product — from raw data cleaning to a live, publicly accessible web app. It was also an opportunity to learn **Streamlit** and gain hands-on experience with **model deployment**.

### Who Is It For?

Anyone curious about property values in British Columbia — homeowners, prospective buyers, or anyone exploring the BC real estate market. No technical knowledge required.

---

## 🌐 Live Demo

**👉 [https://estimai-british-columbia.streamlit.app/](https://estimai-british-columbia.streamlit.app/)**

The app is fully responsive and optimized for both **desktop** and **mobile** devices.

<div align="center">
  <em>Enter an address in British Columbia, fill in property details, and get an instant AI estimate.</em>
</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 📍 **Geocoding & Validation** | Addresses are geocoded via the Geoapify API. Only addresses in British Columbia, Canada are accepted. |
| 🗺️ **Interactive Map** | A map pin is displayed on the entered location for visual confirmation. |
| 🏠 **Comprehensive Property Form** | Users describe property type, square footage, acreage, bedrooms, bathrooms, heating systems, energy sources, parking, and tax information. |
| 🤖 **ML Price Prediction** | A trained Gradient Boosting model returns an estimated market value. |
| 📊 **Confidence Range** | A low/high estimate range is provided, based on the model's Mean Absolute Percentage Error (MAPE) per price segment. |
| 📱 **Mobile Optimized** | Fully responsive UI with CSS media queries for all screen sizes. |
| ❓ **Graceful Missing Data Handling** | Users can indicate "I don't know" for certain fields — the model handles missingness via dedicated indicator features. |

---

## ⚙️ How It Works

```
User enters address & property details
          │
          ▼
  Geoapify API geocodes the address
  (validates: Canada → British Columbia)
          │
          ▼
  Features are assembled into a DataFrame
  (one-hot encoding, missing indicators, etc.)
          │
          ▼
  GradientBoostingRegressor predicts log(price)
          │
          ▼
  exp(prediction) → estimated price in CAD
          │
          ▼
  MAPE-based confidence range is computed
  per price segment
          │
          ▼
  Results displayed with low/high estimates
```

---

## 🧠 Machine Learning Pipeline

### Models Explored

| Model | Outcome |
|---|---|
| Ridge / Lasso / ElasticNet | Underfitting — too simple for this data |
| K-Nearest Neighbors | Poor generalization |
| AdaBoost Regressor | Decent but outperformed by Gradient Boosting |
| Random Forest Regressor | Competitive but higher overfitting risk |
| **Gradient Boosting + DecisionTree** | **✅ Best balance of accuracy and generalization** |

Hyperparameter tuning was performed using **BayesianSearchCV** (via `scikit-optimize`).

### Target Transformation

The target variable (`Price`) was **log-transformed** before training:

$$Y = \ln(1 + \text{Price})$$

This ensures the model penalizes relative errors equally across price ranges — a \$50k error on a \$200k property is treated as more significant than the same error on a \$5M property.

### Final Model Performance

<details>
<summary><strong>📈 Click to see detailed metrics (Train vs. Test)</strong></summary>

| Metric | Test Set | Train Set |
|--------|----------|-----------|
| R² | 0.842 | 0.923 |
| MAE | \$263,672 | \$184,590 |
| RMSE | \$692,304 | \$507,171 |
| MAPE | 14.3% | 10.1% |
| RMSLE | 0.208 | 0.144 |

The gap between train and test scores indicates mild overfitting, which is acceptable given the dataset size and feature complexity.

</details>

### MAPE by Price Range

The model's accuracy was evaluated across five price segments to ensure fair performance at all price levels:

| Price Range (CAD) | MAPE |
|---|---|
| \$64,900 – \$638,000 | 16.8% |
| \$638,000 – \$889,000 | **9.9%** |
| \$889,000 – \$1,327,400 | 11.5% |
| \$1,327,400 – \$2,043,133 | 14.7% |
| \$2,043,133 – \$28,888,000 | 18.7% |

These per-segment MAPE values are used at inference time to provide the **low/high confidence range** displayed in the app.

---

## 📦 Dataset

- **Source:** [Canada Housing Dataset on Kaggle](https://www.kaggle.com/datasets/yuliiabulana/canada-housing) (likely scraped from Zillow or a similar platform)
- **Region:** British Columbia, Canada only
- **Why this dataset?** It is one of the most complete publicly available real estate datasets — far more realistic than toy datasets like California Housing or French government open data.

### Data Engineering

| Stage | Details |
|---|---|
| **Raw data** | ~35,000 rows, 100+ columns (many empty or irrelevant) |
| **After cleaning** | **22,157 rows, 38 columns** |
| **Cleaning steps** | Removed listings with impossible values (e.g., 0 bedrooms for million-dollar homes), dropped columns with >70% missing values, standardized categorical labels |
| **Feature engineering** | Created binary indicator columns for missing values (acreage, tax, parking, heating), one-hot encoded categorical features (property type, heating distribution, energy source) |
| **Target encoding** | Log-transformation: ln(1 + Price) applied before `train_test_split` |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.10+ |
| **ML Framework** | scikit-learn (GradientBoostingRegressor, BayesianSearchCV) |
| **Web App** | Streamlit |
| **Geocoding API** | Geoapify |
| **Data Processing** | Pandas, NumPy |
| **Model Serialization** | Joblib |
| **Deployment** | Streamlit Community Cloud |
| **Notebooks** | Jupyter |

---

## 🗂️ Project Structure

```
canada-housing-predictor/
│
├── app/                              # Streamlit web application
│   ├── streamlit_app.py              # Main app source code
│   ├── estimlogo.png                 # EstimAI logo
│   └── sunny.jpg                     # Hero banner image
│
├── artifacts/                        # Trained models & search results
│   ├── gdb_final_model.pkl           # ✅ Production model (GradientBoosting)
│   ├── gdb_mape_dict.pkl             # MAPE per price range (for confidence intervals)
│   ├── gdb_search.pkl / 2 / 3       # Bayesian search results for GradientBoosting
│   ├── ada_best_model.pkl            # Best AdaBoost model
│   ├── ada_search.pkl / 2 / 3       # AdaBoost search iterations
│   ├── rdf_best_model.pkl            # Best Random Forest model
│   ├── rdf_search.pkl / 2 / 3       # Random Forest search iterations
│   ├── grid_linear.pkl              # Linear regression grid search
│   ├── grid_dtree.pkl               # Decision tree grid search
│   └── grid_trees.pkl               # Tree-based grid search
│
├── data/                             # Data pipeline
│   ├── canada/                       # Raw source data
│   ├── processed/                    # Cleaned & feature-engineered data
│   ├── raw_data_cleaning.ipynb       # Data cleaning notebook
│   └── data_analysis.ipynb           # EDA & analysis notebook
│
├── notebooks/                        # Model training & experimentation
│   ├── Linear_reg.ipynb              # Ridge, Lasso, ElasticNet
│   ├── Random_Forest.ipynb           # Random Forest experiments
│   ├── AdaBoostRegressor.ipynb       # AdaBoost experiments
│   ├── GradientBoostRegressor.ipynb  # ✅ Final model training
│   └── models_analysis.ipynb         # Cross-model comparison
│
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

---

## 🚀 Installation & Local Usage

> **Note:** The app is already live at [estimai-british-columbia.streamlit.app](https://estimai-british-columbia.streamlit.app/). Local installation is only needed if you want to explore the code or retrain models.

### Prerequisites

- Python 3.10+
- A [Geoapify API key](https://www.geoapify.com/) (free tier available)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/canada-housing-predictor.git
cd canada-housing-predictor

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your API key
#    Create a file: .streamlit/secrets.toml
mkdir -p .streamlit
echo 'GEOAPIFY_API_KEY = "your_api_key_here"' > .streamlit/secrets.toml

# 5. Run the app
streamlit run app/streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## ⚠️ Disclaimer

> This tool provides **AI-generated estimates for informational purposes only**. It is **not** a professional appraisal. Actual property values may vary significantly based on market conditions, property condition, and other factors not captured in the model. Always consult a licensed real estate professional for accurate property valuations.

---

<div align="center">

**Built with ❤️ and 🍁 by Marwane**

</div>
