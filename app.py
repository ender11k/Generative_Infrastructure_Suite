import streamlit as st
import pandas as pd
import joblib
import plotly.graph_objects as go
import numpy as np

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Civil AI Master Suite", layout="wide")

# Constants from your original script
ROAD_WIDTH = 12.0
SIDEWALK_WIDTH = 4.0
REAR_SETBACK = 6.0
SIDE_GAP = 5.0
BLOCK_SIZE = 3 # Buildings per block

# --- 2. LOAD BRAIN ---
@st.cache_resource
def load_brain():
    try:
        return joblib.load("civil_ai_brain_rhino.pkl")
    except:
        return None
brain = load_brain()

# --- 3. HELPER FUNCTIONS FOR 3D ---
def get_box_mesh(x, y, z, dx, dy, dz, color):
    """Creates a 3D box for Plotly"""
    return go.Mesh3d(
        x=[x, x+dx, x+dx, x, x, x+dx, x+dx, x],
        y=[y, y, y+dy, y+dy, y, y, y+dy, y+dy],
        z=[z, z, z, z, z-dz, z-dz, z-dz, z-dz],
        i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
        j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
        k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
        color=color,
        opacity=0.8,
        flatshading=True,
        name='Building'
    )

def get_road_mesh(x, y, width, length):
    """Creates a flat road surface"""
    return go.Mesh3d(
        x=[x, x+width, x+width, x],
        y=[y, y, y+length, y+length],
        z=[0, 0, 0, 0], # Roads are at Z=0
        color='#333333', # Dark Grey
        opacity=1.0
    )

# --- 4. UI SIDEBAR ---
st.sidebar.title("🏗️ Civil AI Suite")

# Site Settings
site_w = st.sidebar.slider("Total Site Width (m)", 100, 500, 200)
site_d = st.sidebar.slider("Total Site Depth (m)", 100, 500, 150)

# Lot Settings
lot_width = st.sidebar.number_input("Lot Width", value=40.0)
lot_depth = st.sidebar.number_input("Lot Depth", value=30.0)

# Soil Settings
base_soil = st.sidebar.selectbox("Base Soil", ["Murum", "Black Cotton", "Hard Rock"])

# --- 5. MAIN LOGIC (The Generator) ---
st.header("Site Master Plan Generator")

# Initialize Lists for Plotly
meshes = [] # Stores buildings and roads
lines = []  # Stores pipes

# Calculate Steps
step_x = lot_width + SIDE_GAP
step_y = ROAD_WIDTH + SIDEWALK_WIDTH + lot_depth + REAR_SETBACK
rows = int(site_d / step_y)
cols = int(site_w / step_x)

# --- GENERATE INFRASTRUCTURE (Main Trunk) ---
trunk_x = -15.0
trunk_start_y = site_d + 10
trunk_end_y = -20

# Main Sewer Line (Blue Thick Line)
lines.append(go.Scatter3d(
    x=[trunk_x, trunk_x], y=[trunk_start_y, trunk_end_y], z=[-4, -6],
    mode='lines', line=dict(color='blue', width=8), name='Main Sewer Trunk'
))

# --- GENERATE GRID LOOP ---
total_cost = 0
concrete_vol = 0

for r in range(rows):
    block_y = r * step_y
    road_y = block_y
    building_y = road_y + ROAD_WIDTH + SIDEWALK_WIDTH
    pipe_y = road_y + ROAD_WIDTH + (SIDEWALK_WIDTH/2)
    
    meshes.append(get_road_mesh(0, road_y, site_w, ROAD_WIDTH))
    
    lines.append(go.Scatter3d(
        x=[trunk_x, site_w], y=[pipe_y, pipe_y], z=[-4, -3],
        mode='lines', line=dict(color='cyan', width=4), name='Lateral Pipe'
    ))

    current_x = 0
    for c in range(cols):
        if c > 0 and c % BLOCK_SIZE == 0:
            meshes.append(get_road_mesh(current_x, 0, ROAD_WIDTH, site_d))
            current_x += ROAD_WIDTH
            continue

        # --- AI CALCULATION ---
        sbc = 600 if "Rock" in base_soil else (80 if "Cotton" in base_soil else 250)

        if brain:
            try:
                input_df = pd.DataFrame([{'Derived_Area': lot_width*lot_depth, 'SBC': sbc, 'GW_Depth': 5, 'Soil_Code': 1}])
                pred_thick = brain['model_thick'].predict(input_df)[0] / 1000.0
            except:
                pred_thick = 0.5
        else:
            pred_thick = 1.2 if sbc < 100 else 0.4
            
        # Cost Calc
        vol = lot_width * lot_depth * pred_thick
        concrete_vol += vol
        total_cost += (vol * 7500) # Rate RCC
        
        # --- DRAW BUILDING ---
        fdn_color = '#FF4136' if pred_thick > 0.8 else '#2ECC40'
        meshes.append(get_box_mesh(current_x, building_y, 0, lot_width, lot_depth, pred_thick, fdn_color))
        
        meshes.append(get_box_mesh(current_x, building_y, 0, lot_width, lot_depth, -6.0, '#AAAAAA')) # Negative Z means Up in this function logic, usually distinct

        meshes.append(go.Mesh3d(
            x=[current_x, current_x+lot_width, current_x+lot_width, current_x, current_x, current_x+lot_width, current_x+lot_width, current_x],
            y=[building_y, building_y, building_y+lot_depth, building_y+lot_depth, building_y, building_y, building_y+lot_depth, building_y+lot_depth],
            z=[0, 0, 0, 0, 6, 6, 6, 6], # Height 6m
            i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            color='#DDDDDD', opacity=0.5, name='Warehouse'
        ))

        current_x += step_x

# --- 6. VISUALIZATION ---
fig = go.Figure(data=meshes + lines)

fig.update_layout(
    scene=dict(
        xaxis=dict(title="X (meters)", backgroundcolor="rgb(200, 200, 230)"),
        yaxis=dict(title="Y (meters)", backgroundcolor="rgb(200, 200, 230)"),
        zaxis=dict(title="Z (Elevation)", range=[-10, 10]),
        aspectmode='data' # Keeps the scale 1:1:1 so roads don't look squished
    ),
    margin=dict(l=0, r=0, b=0, t=0),
    height=700
)

st.plotly_chart(fig, use_container_width=True)

# --- 7. METRICS ---
c1, c2, c3 = st.columns(3)
c1.metric("Total Buildings", f"{cols * rows}")
c2.metric("Total Concrete", f"{concrete_vol:.1f} m³")
c3.metric("Project Est. Cost", f"₹{total_cost:,.0f}")