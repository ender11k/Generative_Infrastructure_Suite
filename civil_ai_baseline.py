import matplotlib.pyplot as plt
from shapely.geometry import Polygon
import random
import pandas as pd

# --- SECTION 1: HELPER FUNCTIONS (Physics & Math) ---

def get_rich_soil_data(x, y):
    # 1. Base Zoning Logic
    if x > 350:
        s_type, sbc, color = "Hard Rock", 600, "#7f8c8d"
    elif y > 300:
        s_type, sbc, color = "Black Cotton", 80, "#2c3e50"
    else:
        s_type, sbc, color = "Murum", 250, "#d35400"

    # 2. Add Controlled Noise (15% chance of anomaly)
    if random.random() < 0.15:
        s_type = "Anomaly Pocket"
        sbc = random.choice([75, 550]) 
        color = "#c0392b" # Red alert color

    return {
        "Soil_Type": s_type, "SBC": sbc, "Color": color,
        "N_Value": int(sbc / 10), 
        "GW_Depth": random.uniform(1.5, 8.0),
        "Col_Load": random.randint(800, 1600)
    }

def get_advanced_physics(area, sbc, gw_depth, soil_type):
    # 1. Settlement (Elastic Theory)
    es_map = {"Hard Rock": 50000, "Murum": 15000, "Black Cotton": 5000, "Anomaly Pocket": 7500}
    es = es_map.get(soil_type, 15000) 
    settlement = (sbc * (area**0.5) * 0.8) / es
    
    # 2. Seismic Base Shear
    seismic_coeff = 0.16 
    base_shear = (area * 10) * seismic_coeff
    
    # 3. Hydrostatic Pressure
    water_table_effect = max(0, (10 - gw_depth) * 9.81)
    
    return {
        "Settlement_mm": round(settlement, 2),
        "Seismic_Base_Shear_kN": round(base_shear, 2),
        "Hydrostatic_kPa": round(water_table_effect, 2)
    }

def estimate_materials(area, thickness_mm, pipe_length):
    # 1. Volumes
    concrete_m3 = area * (thickness_mm / 1000)
    steel_kg = concrete_m3 * 80
    excavation_m3 = area * ((thickness_mm / 1000) + 0.5)
    
    # 2. Costs (Pune Rates)
    mats_cost = (concrete_m3 * 7000) + (steel_kg * 70) + (excavation_m3 * 400)
    pipe_cost = pipe_length * 138
    
    return {
        "Concrete_m3": round(concrete_m3, 2),
        "Steel_kg": round(steel_kg, 2),
        "Excavation_m3": round(excavation_m3, 2),
        "Total_Project_Cost_INR": round(mats_cost + pipe_cost, 2)
    }

# --- SECTION 2: SVD ENGINE (Layout) ---

def build_site_plan(total_w, total_d, lot_w, lot_d, road_w, setback=5):
    lots = []
    warehouses = []
    step_x = lot_w + road_w
    step_y = lot_d + road_w
    num_cols = int(total_w / step_x)
    num_rows = int(total_d / step_y)

    for r in range(num_rows):
        for c in range(num_cols):
            x = c * step_x
            y = r * step_y
            lot = Polygon([(x, y), (x + lot_w, y), (x + lot_w, y + lot_d), (x, y + lot_d)])
            warehouse = lot.buffer(-setback)
            lots.append(lot)
            warehouses.append(warehouse)
    return lots, warehouses

def add_drainage_system(total_w, total_d, road_w):
    pond_size = 40 
    pond = Polygon([(total_w - pond_size, 0), (total_w, 0), (total_w, pond_size), (total_w - pond_size, pond_size)])
    main_drain = [(0, road_w/2), (total_w - pond_size, road_w/2), (total_w - pond_size, 0)]
    return pond, main_drain

# --- SECTION 3: DATA FACTORY EXECUTION ---
master_dataset = []
print("🚀 Starting Data Factory Generation...")

for scenario in range(50):
    # Randomize Scenario
    s_width = random.randint(300, 800)
    s_depth = random.randint(300, 800)
    l_w, l_d = random.choice([(60, 40), (80, 50), (100, 60)])
    
    # Generate Layout
    site_lots, site_warehouses = build_site_plan(s_width, s_depth, l_w, l_d, road_w=15)
    pond, main_drain = add_drainage_system(s_width, s_depth, 15)
    
    # Loop Lots
    for i, lot in enumerate(site_lots):
        physics = get_rich_soil_data(lot.centroid.x, lot.centroid.y)
        area = site_warehouses[i].area
        
        # Advanced Physics
        adv_phys = get_advanced_physics(area, physics['SBC'], physics['GW_Depth'], physics['Soil_Type'])
        
        # Logic: Foundation Decision
        if physics['SBC'] < 100:
            found_type, thick = "Raft Slab", (area**0.5) * 22
        elif physics['SBC'] > 400:
            found_type, thick = "Isolated Pad", (area**0.5) * 8
        else:
            found_type, thick = "Standard Slab", (area**0.5) * 15
            
        # Cost Intelligence
        p_length = abs(lot.centroid.y - 7.5)
        costs = estimate_materials(area, thick, p_length)
        
        # Save Data
        master_dataset.append({
            "Scenario_ID": scenario,
            "Site_Size": f"{s_width}x{s_depth}",
            **physics, **adv_phys, **costs,
            "Found_Type": found_type, "Slab_Thickness_mm": thick
        })

# --- SECTION 4: EXPORT & VISUALIZATION ---
df = pd.DataFrame(master_dataset)
df.to_csv("pune_civil_ai_master_data.csv", index=False)
print(f"✅ SUCCESS: Generated {len(df)} rows. Saved to CSV.")

# Visualize the LAST Scenario (Live Re-Generation)
fig, ax = plt.subplots(figsize=(12, 12))

for i, lot in enumerate(site_lots):
    # NOTE: This re-rolls the random soil chance for visualization!
    physics = get_rich_soil_data(lot.centroid.x, lot.centroid.y)
    area = site_warehouses[i].area
    
    # Re-calculate for Labeling
    if physics['SBC'] < 100:
        found_type, thick = "Raft Slab", (area**0.5) * 22
    elif physics['SBC'] > 400:
        found_type, thick = "Isolated Pad", (area**0.5) * 8
    else:
        found_type, thick = "Standard Slab", (area**0.5) * 15

    # Draw
    ax.fill(*lot.exterior.xy, color=physics['Color'], alpha=0.15)
    ax.fill(*site_warehouses[i].exterior.xy, color='#95a5a6', alpha=0.8)
    
    # Label
    ax.text(lot.centroid.x, lot.centroid.y, 
            f"{found_type}\n{thick:.0f}mm\nSBC:{physics['SBC']}", 
            fontsize=6, ha='center', va='center', color='white', fontweight='bold')

# Draw Infrastructure
ax.fill(*pond.exterior.xy, color='#3498db', alpha=0.8, label="Retention Pond")
dx, dy = zip(*main_drain)
ax.plot(dx, dy, color='#27ae60', linestyle='--', linewidth=4, label="Main Pipe")

for lot in site_lots:
    ax.plot([lot.centroid.x, lot.centroid.x], [lot.centroid.y, 7.5], 
            color='#2ecc71', linestyle=':', linewidth=1, alpha=0.7)

ax.set_title(f"Pune Industrial SVD: Final Snapshot ({s_width}x{s_depth}m)")
ax.set_aspect('equal')
plt.legend()
plt.show()