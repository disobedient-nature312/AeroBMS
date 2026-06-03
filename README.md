# 🔋 AeroBMS | NASA Battery Digital Twin

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![XGBoost](https://img.shields.io/badge/XGBoost-AI_Engine-FF9900)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B)

**AeroBMS** is a Physics-Informed Digital Twin and Predictive Maintenance dashboard. It predicts the Remaining Useful Life (RUL) and chemical capacity degradation of Lithium-Ion batteries under aerospace conditions, using an XGBoost model trained on NASA's Prognostics Data Repository.

Instead of predicting abstract time-to-failure labels, this model predicts the **true physical capacity (Ah)** with an MAE of `< 0.15 Ah` on unseen physical batteries, acting as a highly reliable early-warning system.

---

## 🚀 Quick Start (Run the Dashboard)
The pre-trained XGBoost model is already included in this repository. You can launch the Digital Twin dashboard immediately without downloading the raw dataset.

```bash
  # 1. Clone the repository
  git clone https://github.com/Arya-azimi/AeroBMS.git
  cd AeroBMS

  # 2. Install dependencies
  pip install -r requirements.txt

  # 3. Launch the interactive dashboard
  cd app
  streamlit run dashboard.py
```

*The UI will be available at `http://localhost:8501`.*

---

## 🧠 Advanced: Reproducing the Model (Optional)

If you want to run the data engineering pipeline or retrain the AI model from scratch, you will need the raw dataset.

**1. Download the Dataset:**
Download the raw NASA Battery Dataset from Kaggle:
🔗 [NASA Battery Dataset (Kaggle)](https://www.kaggle.com/datasets/patrickfleith/nasa-battery-dataset)
*Extract the CSV files into the `data/cleaned_data/` directory.*

**2. Run the Data Pipeline:**
Extracts physical cycles, calculates true capacity via current integration, and handles sensor noise.

```bash
python scripts/01_data_pipeline.py
```

**3. Train the Model:**
Trains the `XGBRegressor` using custom physical features (Thermal Stress, Voltage Fluctuations).

```bash
python scripts/02_model_training.py
```

---

## 📂 Project Structure

* `app/dashboard.py`: The Streamlit/Plotly Digital Twin UI.
* `models/xgboost_capacity_model.json`: The pre-trained AI weights.
* `scripts/`: Data engineering and model training pipelines.
* `data/`: Contains the sampled test data for dashboard simulation.

---

Developed by Arya Azimi