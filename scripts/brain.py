#! python3
# r: pandas
# r: scikit-learn
# r: joblib

import rhinoscriptsyntax as rs
import pandas as pd
import joblib
import random
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

# --- 1. GENERATE TRAINING DATA (Internally) ---
print("🧠 Generating Training Data inside Rhino...")

data = []
soils = ["Black Cotton", "Murum", "Hard Rock", "Sandy Soil"]

for _ in range(2000): # Create 2000 synthetic records
    soil = random.choice(soils)
    area = random.randint(500, 5000)
    
    # Engineering Logic (The "Truth")
    if soil == "Black Cotton":
        sbc = 80
        # Bad soil needs thick foundation
        thick = random.randint(750, 950) 
        cost_base = 2500
    elif soil == "Hard Rock":
        sbc = 600
        # Good soil needs thin foundation
        thick = random.randint(150, 250)
        cost_base = 800
    else: # Murum / Sandy
        sbc = 250
        thick = random.randint(400, 500)
        cost_base = 1200
        
    # Add noise/variation
    total_cost = (area * cost_base) + random.randint(-50000, 50000)
    
    data.append({
        'Soil_Type': soil,
        'Slab_Thickness_mm': thick,
        'Total_Project_Cost_INR': total_cost,
        'Concrete_m3': (area * thick) / 1000,
        'Derived_Area': area,
        'SBC': sbc,
        'GW_Depth': 5.0
    })

df = pd.DataFrame(data)

# --- 2. TRAIN THE BRAIN ---
print("🎓 Training Random Forest Model...")

# Encode Soil
le = LabelEncoder()
df['Soil_Code'] = le.fit_transform(df['Soil_Type'])

# Features & Targets
X = df[['Derived_Area', 'SBC', 'GW_Depth', 'Soil_Code']]
y_thick = df['Slab_Thickness_mm']
y_cost = df['Total_Project_Cost_INR']

# Train
model_thick = RandomForestRegressor(n_estimators=50) # Light version for Rhino
model_thick.fit(X, y_thick)

model_cost = RandomForestRegressor(n_estimators=50)
model_cost.fit(X, y_cost)

# --- 3. SAVE THE COMPATIBLE BRAIN ---
brain_packet = {
    'model_thick': model_thick,
    'model_cost': model_cost,
    'soil_map': dict(zip(le.classes_, range(len(le.classes_))))
}

# Save to D:\Archi (Or C:\Archi if D doesn't exist)
save_path = r"D:\Archi\civil_ai_brain_rhino.pkl"
try:
    joblib.dump(brain_packet, save_path)
    print(f"✅ SUCCESS: Compatible Brain saved to: {save_path}")
    rs.MessageBox(f"Brain Trained & Saved!\nLocation: {save_path}", 0, "Success")
except Exception as e:
    rs.MessageBox(f"Error saving file: {e}", 0, "Error")