# 🏗️ Generative Infrastructure Suite

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-FF4B4B)
![Scikit-Learn](https://img.shields.io/badge/AI-Scikit--Learn-orange)
![Plotly](https://img.shields.io/badge/Visualization-Plotly-3F4F75)

**An AI-powered design assistant for Civil Engineers and Architects.**

The **Generative Infrastructure Suite** is a web-based application that automates the creation of industrial master plans. By combining Machine Learning with parametric design, it allows users to instantly generate 3D layouts, predict foundation requirements based on soil conditions, and calculate real-time cost estimates (BOQ).

## 🚀 Live Demo
**[Click here to try the app live!](https://generativeinfra.streamlit.app)**
*(Note: If the link is not active, the project is likely running locally. See Installation steps below.)*

## ✨ Key Features

* **🤖 AI Foundation Prediction:** Uses a trained Machine Learning model (`RandomForestRegressor`) to predict the required foundation depth based on soil type (SBC) and structural load.
* **city-scale Generation:** Parametrically generates roads, drainage networks (main trunk & laterals), and building plots based on user-defined site dimensions.
* **interactive 3D Visualization:** Fully interactive 3D view of the master plan using **Plotly**, allowing engineers to inspect the site from any angle.
* **💰 Automated BOQ:** Instantly calculates the Bill of Quantities (Concrete Volume, Excavation, Steel) and estimates the total project cost in real-time.
* **Dynamic Soil Context:** "Smart Foundation" visualization changes color and depth dynamically (Red = Deep/Risky, Green = Shallow/Stable) based on the selected soil profile.

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (Web UI)
* **Visualization:** [Plotly](https://plotly.com/) (3D Meshing & Rendering)
* **Machine Learning:** [Scikit-Learn](https://scikit-learn.org/) (Regression Model for Structural Analysis)
* **Data Processing:** Pandas & NumPy
* **Backend Logic:** Python

## 📦 Installation & Local Run

Want to run this on your own machine? Follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/ender11k/Generative_Infrastructure_Suite.git](https://github.com/ender11k/Generative_Infrastructure_Suite.git)
    cd Generative_Infrastructure_Suite
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

4.  **Open your browser:**
    The app should automatically open at `http://localhost:8501`.

