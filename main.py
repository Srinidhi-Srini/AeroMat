import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from typing import NamedTuple

df = pd.read_csv("materials.csv")
df["specific_strength"] = df["yield_strength"] / df["density"]
df["specific_stiffness"] = df["elastic_modulus"] / df["density"]

class MaterialProp(NamedTuple):
    material: str
    density: float 
    yield_strength: float
    ultimate_tensile_strength: float
    elastic_modulus: float
    thermal_conductivity: float
    max_service_temp: float
    specific_strength: float
    specific_stiffness: float

materials_list: dict[str, MaterialProp] = {}
for index, row in df.iterrows():
    name = str(row['material'])
    materials_list[name] = MaterialProp(
        material = name,
        density = float(row['density']),
        yield_strength = float(row['yield_strength']),
        ultimate_tensile_strength = float(row['ultimate_tensile_strength']),
        elastic_modulus = float(row['elastic_modulus']),
        thermal_conductivity = float(row['thermal_conductivity']),
        max_service_temp = float(row['max_service_temp']),
        specific_strength = float(row['specific_strength']),
        specific_stiffness = float(row['specific_stiffness'])
    )


def material_table():
    print(df.to_string())

def user_material_ver1():
    try:
        target_density = float(input("Enter your desired density (in g/cm^3): "))
        target_yield_strength = float(input("Enter your desired yield strength (in MPa): "))
        # target_ultimate_tensile_strength = float(input("Enter your desired ultimate tensile strength (in MPa): "))
        # target_elastic_modulus = float(input("Enter your desired elastic modulus (in GPa): "))
        # target_thermal_conductivity = float(input("Enter your desired thermal conductivity (W/m-K): "))
        target_max_service_temp = float(input("Enter your desired maximum service temperature (C): "))
        target_similarity = float(input("Entire your desired minimum similarity score (1-100): "))
    except:
        print("Invalid input. Please enter a number.")
        return


    def difference(item):
        prop = item[1]
        diff_density = abs(prop.density - target_density)/(target_density)     
        diff_yield_strength = abs(prop.yield_strength - target_yield_strength)/(target_yield_strength)
        # diff_ultimate_tensile_strength = abs(prop.ultimate_tensile_strength - target_ultimate_tensile_strength)/(target_ultimate_tensile_strength)
        # diff_elastic_modulus = abs(prop.elastic_modulus - target_elastic_modulus)/(target_elastic_modulus)
        # diff_thermal_conductivity = abs(prop.thermal_conductivity - target_thermal_conductivity) / (target_thermal_conductivity)
        diff_max_service_temp = abs(prop.max_service_temp - target_max_service_temp) / (target_max_service_temp)
        
        return diff_density + diff_yield_strength + diff_max_service_temp 

    best_match = sorted(materials_list.items(), key = difference)
    print("="*50)
    print(f"Matched Materials within {target_similarity:.1f}% Target Similarity: ")
    print(f"""Density: {target_density} g/cm^3 | Yield Strength: {target_yield_strength} MPa | Maximum Service Temperature: {target_max_service_temp} C """ )
    
    print("="*50)
    for rank, (material, prop) in enumerate(best_match, 1):
        score = difference((material, prop))
        similarity = max(0.0, (1.0 - (score / 3.0)) * 100)
        if similarity >= target_similarity: 
            print(f"{rank}. {material} ({similarity:.1f}% Match)")
            print(f"Density: {prop.density} g/cm^3")
            print(f"Yield Strength: {prop.yield_strength} MPa")
            print(f"Ultimate Tensile Strength: {prop.ultimate_tensile_strength} MPa")
            print(f"Elastic Modulus: {prop.elastic_modulus} GPa")
            print(f"Thermal Conductivity: {prop.thermal_conductivity} W/m*K")
            print(f"Maximum Service Temperature: {prop.max_service_temp} C")
            print(f"Specific Strength: {prop.specific_strength:.1f} N*m/kg")
            print(f"Specific Stiffness: {prop.specific_stiffness:.1f} N*m/kg")
            print("="*50)

def user_material_ver2():
    try:
        max_density = float(input("Enter your desired maximum density (in g/cm^3): "))
        min_yield_strength = float(input("Enter your desired minimum yield strength (in MPa): "))
        min_service_temp = float(input("Enter your desired minimum service temperature (C): "))
    except:
        print("Invalid input. Please enter a number.")
        return

    filtered_df = df[(df['density'] <= max_density) & 
                     (df['yield_strength'] >= min_yield_strength) & 
                     (df['max_service_temp'] >= min_service_temp)].copy()
    if filtered_df.empty:
        print("No matching materials found. ")
        return
    
    filtered_df['specific_strength'] = filtered_df['yield_strength'] / filtered_df['density']
    filtered_df['specific_stiffness'] = filtered_df['elastic_modulus'] / filtered_df['density']

    filtered_df['norm_specific_strength'] = (filtered_df['specific_strength'] - filtered_df['specific_strength'].min()) / (filtered_df['specific_strength'].max() - filtered_df['specific_strength'].min())
    filtered_df['norm_specific_stiffness'] = (filtered_df['specific_stiffness'] - filtered_df['specific_stiffness'].min()) / (filtered_df['specific_stiffness'].max() - filtered_df['specific_stiffness'].min())
    filtered_df["score"] = (filtered_df['norm_specific_strength'] * 0.5) + (filtered_df['norm_specific_stiffness'] * 0.5)

    sorted_df = filtered_df.sort_values(by="score", ascending=False)
    if len(filtered_df) == 1:
        sorted_df = filtered_df
        sorted_df["score"] = 1.0

    print("="*50)
    print(f"Matched Materials: ")
    print(f"""Density: {max_density} g/cm^3 | Yield Strength: {min_yield_strength} MPa | Maximum Service Temperature: {min_service_temp} C """ )
    
    print("="*50)
    for rank, (index, row) in enumerate(sorted_df.iterrows(), 1):
        print(f"{rank}. {row['material']} Score: {row['score']:.3f}")
        print(f"*Density: {row['density']} g/cm^3*")
        print(f"*Yield Strength: {row['yield_strength']} MPa*")
        print(f"*Maximum Service Temperature: {row['max_service_temp']} C*")
        print(f"Ultimate Tensile Strength: {row['ultimate_tensile_strength']} MPa")
        print(f"Elastic Modulus: {row['elastic_modulus']} GPa")
        print(f"Thermal Conductivity: {row['thermal_conductivity']} W/m*k")
        print(f"Specific Strength: {row['specific_strength']:.1f} N*m/kg")
        print(f"Specific Stiffness: {row['specific_stiffness']:.1f} N*m/kg")
        print("="*50)


while True:
    choice = input("Press (1) to view materials database, (2) to match properties by similarity, (3) to match properties by min/max requirements or (Q) to quit: ").strip().upper()

    if choice == "1":
        material_table()
    elif choice == "2":
        user_material_ver1()
    elif choice == "3":
        user_material_ver2()
    elif choice == "Q":
        print("Quitting program.")
        break
    else:
        print("Invalid choice. Please try again. ")