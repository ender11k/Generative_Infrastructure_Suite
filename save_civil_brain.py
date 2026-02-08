import pandas as pd
import joblib  # Standard library for saving ML models
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

# 1. Load Data
df = pd.read_csv('pune_civil_ai_master_data.csv')

# 2. Feature Engineering (Re-creating the Area feature)
df['Derived_Area'] = df['Concrete_m3'] / (df['Slab_Thickness_mm'] / 1000)

# 3. Encode Data
le = LabelEncoder()
df['Soil_Code'] = le.fit_transform(df['Soil_Type'])

# 4. Train Model (Predicting Thickness AND Cost)
# We will train two separate "Lobes" of the brain
X = df[['Derived_Area', 'SBC', 'GW_Depth', 'Soil_Code']]

model_cost = RandomForestRegressor(n_estimators=100)
model_cost.fit(X, df['Total_Project_Cost_INR'])

model_thick = RandomForestRegressor(n_estimators=100)
model_thick.fit(X, df['Slab_Thickness_mm'])

# 5. Save the "Brain" to a file
brain_packet = {
    'model_cost': model_cost,
    'model_thick': model_thick,
    'soil_encoder': le,
    'soil_map': dict(zip(le.classes_, range(len(le.classes_))))
}

joblib.dump(brain_packet, 'civil_ai_brain.pkl')
print("✅ Brain saved as 'civil_ai_brain.pkl'. Move this file to your Rhino folder.")