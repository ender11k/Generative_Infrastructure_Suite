#! python3
# r: pandas
# r: scikit-learn
# r: joblib

import rhinoscriptsyntax as rs
import joblib
import pandas as pd
import os

# --- CONFIGURATION ---
BRAIN_PATH = r"D:\Archi\civil_ai_brain_rhino.pkl" 
COST_PATH = r"D:\Archi\Civil_AI_BOQ_Cost.csv"
DESIGN_PATH = r"D:\Archi\Civil_AI_Design_Log.csv"

# Layout
LOT_WIDTH = 40.0   
LOT_DEPTH = 30.0   
ROAD_WIDTH = 12.0  
SIDEWALK_WIDTH = 4.0 

REAR_SETBACK = 6.0    
SIDE_GAP = 5.0        
BLOCK_SIZE = 3        

# Infrastructure
LATERAL_DIA = 0.8  
MAIN_DIA = 3.0     
POND_RADIUS = 25.0 
SLOPE_PCT = 1.5    

# Detailed Rates (INR)
RATE_EXCAVATION = 350.0   
RATE_BACKFILLING = 200.0  
RATE_PCC = 4500.0         
RATE_RCC_M25 = 7500.0     
RATE_STEEL = 85.0         
KG_STEEL_PER_M3 = 110.0   

RATE_ROAD_BASE = 850.0    
RATE_ROAD_ASPHALT = 650.0 
RATE_PAVER_BLOCK = 900.0  

RATE_PIPE_LAT = 2800.0    
RATE_PIPE_MAIN = 8500.0   
RATE_MANHOLE = 18000.0    

def load_brain():
    if not os.path.exists(BRAIN_PATH):
        rs.MessageBox("Brain file missing!", 0, "Error")
        return None
    return joblib.load(BRAIN_PATH)

def get_soil_name_interactive(brain, prompt_text="Select Soil Type"):
    original_keys = list(brain['soil_map'].keys())
    rhino_safe_map = {k.replace(" ", "_"): k for k in original_keys}
    safe_options = list(rhino_safe_map.keys())
    user_input = rs.GetString(f"🤖 AI: {prompt_text}?", "Murum", strings=safe_options)
    if not user_input: return "Murum"
    return rhino_safe_map.get(user_input, user_input)

def is_point_in_box(pt, corners):
    # Extract all X and Y coordinates from the 4 corners to find true bounds
    xs = [p[0] for p in corners]
    ys = [p[1] for p in corners]
    
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    # Check if the point is within the min/max bounds
    return (min_x <= pt[0] <= max_x) and (min_y <= pt[1] <= max_y)

def civil_ai_master_suite():
    brain = load_brain()
    if not brain: return
    
    # 1. SETUP LAYERS
    layers = [
        ("AI_Roads", [50, 50, 50]),       
        ("AI_Utility_Corridor", [180, 180, 180]), 
        ("AI_Drainage_Lat", [0, 150, 255]), 
        ("AI_Drainage_Main", [0, 0, 139]),  
        ("AI_Water_Pond", [0, 255, 255]),   
        ("AI_Fdn_Good", [50, 200, 50]),   
        ("AI_Fdn_Bad", [200, 50, 50]),    
        ("AI_Buildings", [200, 200, 200]),
        ("AI_Roof", [150, 150, 150]),
        ("AI_Zones", [255, 255, 0])
    ]
    for name, color in layers:
        if not rs.IsLayer(name): rs.AddLayer(name, color)

    # 2. SITE INPUT
    print("🏙️  Generating Professional Project Suite...")
    rs.MessageBox("Step 1: Draw Master Plan Boundary.", 0, "Input")
    
    rect_points = rs.GetRectangle(1) 
    if not rect_points: return
    
    p1, p3 = rect_points[0], rect_points[2]
    site_w = abs(p3.X - p1.X)
    site_d = abs(p3.Y - p1.Y)
    origin = [min(p1.X, p3.X), min(p1.Y, p3.Y), 0]
    
    rs.ZoomExtents()

    # 3. ZONES
    base_soil = get_soil_name_interactive(brain, "Base Soil")
    special_zones = [] 
    while True:
        add_zone = rs.GetString("Add Soil Zone?", "No", strings=["Yes", "No"])
        if not add_zone or add_zone != "Yes": break
        z_rect = rs.GetRectangle(1) 
        if z_rect:
            rs.CurrentLayer("AI_Zones")
            rs.AddPolyline([z_rect[0], z_rect[1], z_rect[2], z_rect[3], z_rect[0]])
            zone_soil = get_soil_name_interactive(brain, "Soil Type for this Zone")
            special_zones.append((z_rect, zone_soil))
            
            # Label the zone center
            center = [(z_rect[0].X + z_rect[2].X)/2, (z_rect[0].Y + z_rect[2].Y)/2, origin[2]]
            rs.AddTextDot(zone_soil, center)

    # 4. GENERATE
    rs.EnableRedraw(False)
    boq_data = []      # For Cost Report
    design_log = []    # For Technical Report

    step_x_build = LOT_WIDTH + SIDE_GAP
    step_y = ROAD_WIDTH + SIDEWALK_WIDTH + LOT_DEPTH + REAR_SETBACK
    rows = int(site_d / step_y)
    
    print("🏗️  Processing Engineering Calculations...")

    # --- A. INFRASTRUCTURE ---
    rs.CurrentLayer("AI_Drainage_Main")
    trunk_x = origin[0] - 15.0 
    trunk_start_y = origin[1] + site_d + 10
    trunk_end_y = origin[1] - 20
    trunk_len = abs(trunk_start_y - trunk_end_y)
    trunk_drop = trunk_len * (SLOPE_PCT / 100.0)
    z_trunk_top = origin[2] - 4.0
    z_trunk_btm = z_trunk_top - trunk_drop 
    
    main_crv = rs.AddLine([trunk_x, trunk_start_y, z_trunk_top], [trunk_x, trunk_end_y, z_trunk_btm])
    rs.AddPipe(main_crv, 0, MAIN_DIA, cap=0)
    rs.DeleteObject(main_crv)
    
    boq_data.append({"Category": "Infrastructure", "Item": "Main Trunk Sewer", "Unit": "m", "Qty": trunk_len, "Rate": RATE_PIPE_MAIN})
    trunk_excav = trunk_len * 5.0 * 4.0
    boq_data.append({"Category": "Earthwork", "Item": "Trunk Excavation", "Unit": "m3", "Qty": trunk_excav, "Rate": RATE_EXCAVATION})

    rs.CurrentLayer("AI_Water_Pond")
    pond_center = [trunk_x, trunk_end_y - POND_RADIUS, 0]
    rs.AddCylinder([pond_center[0], pond_center[1], z_trunk_btm - 2], 3.0, POND_RADIUS)
    pond_vol = 3.14 * (POND_RADIUS**2) * 5.0
    boq_data.append({"Category": "Earthwork", "Item": "Pond Excavation", "Unit": "m3", "Qty": pond_vol, "Rate": RATE_EXCAVATION})

    # --- B. GRID LOOP ---
    for r in range(rows):
        block_y = origin[1] + (r * step_y)
        road_y_start = block_y
        sidewalk_y_start = road_y_start + ROAD_WIDTH
        building_y_start = sidewalk_y_start + SIDEWALK_WIDTH
        pipe_y = sidewalk_y_start + (SIDEWALK_WIDTH / 2)
        
        ratio = (trunk_start_y - pipe_y) / trunk_len
        z_row_start = z_trunk_top - (trunk_drop * ratio)

        # Feeder Pipe
        rs.CurrentLayer("AI_Drainage_Lat")
        rise_feeder = 15.0 * (SLOPE_PCT / 100.0)
        z_city_start = z_row_start + rise_feeder
        feeder_pipe = rs.AddLine([trunk_x, pipe_y, z_row_start], [origin[0], pipe_y, z_city_start])
        rs.AddPipe(feeder_pipe, 0, LATERAL_DIA, cap=0)
        rs.DeleteObject(feeder_pipe)
        boq_data.append({"Category": "Infrastructure", "Item": "Feeder Pipe", "Unit": "m", "Qty": 15.0, "Rate": RATE_PIPE_LAT})

        current_x = origin[0]
        col_count = 0
        
        while current_x < (origin[0] + site_w - step_x_build):
            
            # VERTICAL ROAD
            if col_count > 0 and col_count % BLOCK_SIZE == 0:
                rs.CurrentLayer("AI_Roads")
                rs.AddSrfPt([[current_x, origin[1], origin[2]], [current_x + ROAD_WIDTH, origin[1], origin[2]], [current_x + ROAD_WIDTH, origin[1] + site_d, origin[2]], [current_x, origin[1] + site_d, origin[2]]])
                
                rs.CurrentLayer("AI_Drainage_Lat")
                dist_x = current_x - trunk_x
                rise_start = dist_x * (SLOPE_PCT / 100.0)
                rise_end = (dist_x + ROAD_WIDTH) * (SLOPE_PCT / 100.0)
                bridge_pipe = rs.AddLine([current_x, pipe_y, z_row_start + rise_start], 
                                         [current_x + ROAD_WIDTH, pipe_y, z_row_start + rise_end])
                rs.AddPipe(bridge_pipe, 0, LATERAL_DIA, cap=0)
                rs.DeleteObject(bridge_pipe)
                boq_data.append({"Category": "Infrastructure", "Item": "Street Pipe", "Unit": "m", "Qty": ROAD_WIDTH, "Rate": RATE_PIPE_LAT})

                current_x += ROAD_WIDTH 
                col_count += 1 
                continue 
            
            # STANDARD LOT
            ox = current_x
            oy = building_y_start
            oz = origin[2]
            
            # Road
            rs.CurrentLayer("AI_Roads")
            rs.AddSrfPt([[ox, road_y_start, oz], [ox + step_x_build, road_y_start, oz], [ox + step_x_build, road_y_start + ROAD_WIDTH, oz], [ox, road_y_start + ROAD_WIDTH, oz]])
            road_area = step_x_build * ROAD_WIDTH
            boq_data.append({"Category": "Roads", "Item": "Asphalt Road", "Unit": "sqm", "Qty": road_area, "Rate": RATE_ROAD_ASPHALT})
            
            # Sidewalk
            rs.CurrentLayer("AI_Utility_Corridor")
            rs.AddSrfPt([[ox, sidewalk_y_start, oz], [ox + step_x_build, sidewalk_y_start, oz], [ox + step_x_build, building_y_start, oz], [ox, building_y_start, oz]])
            
            # Pipe
            rs.CurrentLayer("AI_Drainage_Lat")
            dist_x = ox - trunk_x
            z_pipe_start = z_row_start + (dist_x * (SLOPE_PCT / 100.0))
            z_pipe_end = z_row_start + ((dist_x + step_x_build) * (SLOPE_PCT / 100.0))
            seg_crv = rs.AddLine([ox, pipe_y, z_pipe_start], [ox + step_x_build, pipe_y, z_pipe_end])
            rs.AddPipe(seg_crv, 0, LATERAL_DIA, cap=0)
            rs.DeleteObject(seg_crv)
            boq_data.append({"Category": "Infrastructure", "Item": "Street Pipe", "Unit": "m", "Qty": step_x_build, "Rate": RATE_PIPE_LAT})
            
            # --- AI BUILDING ---
            center_pt = [ox + LOT_WIDTH/2, oy + LOT_DEPTH/2, oz]
            current_soil = base_soil
            for corners, s_name in reversed(special_zones):
                if is_point_in_box(center_pt, corners):
                    current_soil = s_name
                    break
            
            soil_code = brain['soil_map'].get(current_soil, 0)
            s_check = str(current_soil)
            sbc = 600 if "Rock" in s_check else (80 if "Cotton" in s_check else 250)
            
            input_df = pd.DataFrame([{ 'Derived_Area': LOT_WIDTH * LOT_DEPTH, 'SBC': sbc, 'GW_Depth': 5.0, 'Soil_Code': soil_code }])
            pred_thick = brain['model_thick'].predict(input_df)[0] / 1000.0
            
            # Geometry
            layer = "AI_Fdn_Bad" if pred_thick > 0.8 else "AI_Fdn_Good"
            rs.CurrentLayer(layer)
            rs.AddBox([[ox, oy, oz], [ox+LOT_WIDTH, oy, oz], [ox+LOT_WIDTH, oy+LOT_DEPTH, oz], [ox, oy+LOT_DEPTH, oz], [ox, oy, oz-pred_thick], [ox+LOT_WIDTH, oy, oz-pred_thick], [ox+LOT_WIDTH, oy+LOT_DEPTH, oz-pred_thick], [ox, oy+LOT_DEPTH, oz-pred_thick]])
            rs.CurrentLayer("AI_Buildings")
            rs.AddBox([[ox, oy, oz], [ox+LOT_WIDTH, oy, oz], [ox+LOT_WIDTH, oy+LOT_DEPTH, oz], [ox, oy+LOT_DEPTH, oz], [ox, oy, oz+6.0], [ox+LOT_WIDTH, oy, oz+6.0], [ox+LOT_WIDTH, oy+LOT_DEPTH, oz+6.0], [ox, oy+LOT_DEPTH, oz+6.0]])
            rs.CurrentLayer("AI_Roof")
            mid_y = oy + (LOT_DEPTH/2)
            rs.AddSrfPt([[ox, oy, oz+6], [ox+LOT_WIDTH, oy, oz+6], [ox+LOT_WIDTH, mid_y, oz+8.5], [ox, mid_y, oz+8.5]]) 
            rs.AddSrfPt([[ox, mid_y, oz+8.5], [ox+LOT_WIDTH, mid_y, oz+8.5], [ox+LOT_WIDTH, oy+LOT_DEPTH, oz+6], [ox, oy+LOT_DEPTH, oz+6]]) 

            # --- CALCULATIONS ---
            # 1. Quantities
            pit_vol = (LOT_WIDTH+2)*(LOT_DEPTH+2)*(pred_thick+0.15)
            rcc_vol = LOT_WIDTH * LOT_DEPTH * pred_thick
            steel_kg = rcc_vol * KG_STEEL_PER_M3
            
            # 2. Add to Cost Report (BOQ)
            boq_data.append({"Category": "Structure", "Item": "Fdn Concrete", "Unit": "m3", "Qty": rcc_vol, "Rate": RATE_RCC_M25})
            boq_data.append({"Category": "Structure", "Item": "Fdn Steel", "Unit": "kg", "Qty": steel_kg, "Rate": RATE_STEEL})
            boq_data.append({"Category": "Earthwork", "Item": "Excavation", "Unit": "m3", "Qty": pit_vol, "Rate": RATE_EXCAVATION})
            
            # 3. Add to Design Log (Technical Report)
            design_log.append({
                "Building_ID": f"Row{r+1}_Col{col_count+1}",
                "Soil_Type": current_soil,
                "SBC_Value": sbc,
                "AI_Thickness_mm": int(pred_thick * 1000),
                "Excavation_Depth_m": round(pred_thick + 0.15, 2),
                "Concrete_Vol_m3": round(rcc_vol, 1),
                "Steel_Req_kg": int(steel_kg)
            })

            current_x += step_x_build
            col_count += 1

    rs.EnableRedraw(True)
    rs.ZoomExtents()
    
    # --- SAVE FILES ---
    # 1. COST REPORT
    df_boq = pd.DataFrame(boq_data)
    summary = df_boq.groupby(['Category', 'Item', 'Unit', 'Rate'])['Qty'].sum().reset_index()
    summary['Total'] = summary['Qty'] * summary['Rate']
    summary.to_csv(COST_PATH, index=False)
    
    # 2. DESIGN LOG
    df_log = pd.DataFrame(design_log)
    df_log.to_csv(DESIGN_PATH, index=False)
    
    rs.MessageBox(f"✅ PROJECT COMPLETE\n\n1. BOQ Cost Report: {COST_PATH}\n2. Design Log: {DESIGN_PATH}", 0, "Success")
    os.startfile(COST_PATH)
    os.startfile(DESIGN_PATH)

if __name__ == "__main__":
    civil_ai_master_suite()