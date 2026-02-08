import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder

# --- STEP 1: LOAD & PREPARE BRAIN ---
print("🧠 Loading Engineering Knowledge...")
df = pd.read_csv('pune_civil_ai_master_data.csv')

# FEATURE ENGINEERING: Recovering 'Area' from Physics
# Since we didn't save Area directly, we derive it: Area = Concrete / (Thickness/1000)
df['Derived_Area'] = df['Concrete_m3'] / (df['Slab_Thickness_mm'] / 1000)

# Encode Soil Types (Text -> Numbers)
le = LabelEncoder()
df['Soil_Code'] = le.fit_transform(df['Soil_Type'])
soil_map = dict(zip(le.classes_, range(len(le.classes_))))

print(f"   Data Loaded: {len(df)} projects found.")
print(f"   Soil Types Learned: {list(soil_map.keys())}")

# --- STEP 2: TRAIN THE MODEL ---
# Features: Area, Soil Strength (SBC), Groundwater, Load
X = df[['Derived_Area', 'SBC', 'GW_Depth', 'Col_Load', 'Soil_Code']]
# Target: Total Money
y = df['Total_Project_Cost_INR']

# Split data (80% for training, 20% for testing)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the "Random Forest" (A collection of decision trees)
print("🤖 Training the Neural Pathways (Random Forest)...")
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
score = model.score(X_test, y_test)
print(f"✅ Training Complete. AI Accuracy Score: {score:.4f} (1.0 is perfect)")

# --- STEP 3: THE PREDICTION ENGINE ---
def predict_new_project(area_sqm, soil_type, sbc, gw_depth=5.0):
    # Convert text soil type to the number the AI understands
    soil_code = soil_map.get(soil_type, 0) # Default to 0 if unknown
    
    # Create the input packet
    input_data = pd.DataFrame([{
        'Derived_Area': area_sqm,
        'SBC': sbc,
        'GW_Depth': gw_depth,
        'Col_Load': 1200, # Average load
        'Soil_Code': soil_code
    }])
    
    # Ask the AI
    predicted_price = model.predict(input_data)[0]
    return predicted_price

# --- STEP 4: LIVE DEMO ---
print("-" * 40)
print("🔮 AI PREDICTION DEMO: 1000 sqm Warehouse")
print("-" * 40)

# Scenario A: Good Ground
cost_rock = predict_new_project(1000, "Hard Rock", 600)
print(f"🏗️  On Hard Rock (SBC 600):  ₹{cost_rock:,.2f}")

# Scenario B: Bad Ground
cost_mud = predict_new_project(1000, "Black Cotton", 80)
print(f"🌧️  On Black Cotton (SBC 80): ₹{cost_mud:,.2f}")

diff = cost_mud - cost_rock
print(f"\n⚠️  Risk Cost: You will pay ₹{diff:,.2f} extra for the bad soil.")
print("-" * 40)