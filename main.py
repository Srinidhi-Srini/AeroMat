import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from typing import NamedTuple

df = pd.read_csv("materials.csv")

class MaterialProp(NamedTuple):
    material: str
    density: float 
    yield_strength: float
    ultimate_tensile_strength: float
    elastic_modulus: float
    thermal_conductivity: float
    max_service_temp: float

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
        max_service_temp = float(row['max_service_temp'])
    )

# def density_inc():
#     sorted_density_dec = sorted(
#         materials_list.items(), key=lambda item: item[1].density
#     )

#     print("\nMaterials sorted by increasing density:")
#     # Use * _ to grab all remaining elements of the tuple, keeping prop intact
#     for material, (name, density, *_) in sorted_density_dec:
#         print(f"{material}: {density} g/cm^3")


# def yield_strength_inc():
#     sorted_yield_strength_dec = sorted(
#         materials_list.items(), key=lambda item: item[1].yield_strength,
#     )

#     print("\nMaterials sorted by increasing yield strength:")
#     # Same here: unpacks the internal named tuple values cleanly
#     for material, (name, _, yield_strength, *_) in sorted_yield_strength_dec:
#         print(f"{material}: {yield_strength} MPa")

# def elastic_modulus_inc():
#     sorted_elastic_modulus_dec = sorted(
#         materials_list.items(), key=lambda item: item[1].elastic_modulus,
#     )

#     print("\nMaterials sorted by increasing elastic modulus:")
#     for material, (name, _, _, elastic_modulus) in sorted_elastic_modulus_dec:
#         print(f"{material}: {elastic_modulus} GPa")

# def user_density():
#     try:
#         user_density = float(input("Enter your desired density (in g/cm^3): "))
#     except:
#         print("Invalid input. Please enter a number.")
#         return

#     closest_density = sorted(materials_list.items(), key = lambda item:abs(item[1].density - user_density))

#     print(f"The materials closest to your desired density of {user_density} g/cm^3: ")
#     for material, (name, density, *_) in closest_density:
#         print(f"{material}: {density}")

# def user_yield_strength():
#     try:
#         user_yield_strength = float(input("Enter your desired yield strength (in MPa): "))
#     except:
#         print("Invalid input. Please enter a number.")
#         return

#     closest_yield_strength = sorted(materials_list.items(), key = lambda item:abs(item[1].yield_strength - user_yield_strength))
#     print(f"The materials closest to your desired yield strength of {user_yield_strength} MPa: ")
#     for material, (name, _, yield_strength, _) in closest_yield_strength:
#         print(f"{material}: {yield_strength}")

# def user_elastic_modulus():
#     try: 
#         user_elastic_modulus = float(input("Enter your desired elastic modulus (in GPa): "))
#     except:
#         print("Invalid input. Please enter a number.")
#         return
    
#     closest_elastic_modulus = sorted(materials_list.items(), key = lambda item: abs(item[1].elastic_modulus - user_elastic_modulus))
#     print(f"The materials closest to your desired elastic modulus  of {user_elastic_modulus} GPa: ")
#     for material, (name, _, _, elastic_modulus) in closest_elastic_modulus:
#         print(f"{material}: {elastic_modulus}")

def material_table():
    print(df.to_string())

def user_material():
    try:
        target_density = float(input("Enter your desired density (in g/cm^3): "))
        target_yield_strength = float(input("Enter your desired yield strength (in MPa): "))
        target_ultimate_tensile_strength = float(input("Enter your desired ultimate tensile strength (in MPa): "))
        target_elastic_modulus = float(input("Enter your desired elastic modulus (in GPa): "))
        target_thermal_conductivity = float(input("Enter your desired thermal conductivity (W/m-K): "))
        target_max_service_temp = float(input("Enter your desired maximum service temperature (C): "))
    except:
        print("Invalid input. Please enter a number.")
        return

    def difference(item):
        prop = item[1]
        diff_density = abs(prop.density - target_density)/(target_density)     
        diff_yield_strength = abs(prop.yield_strength - target_yield_strength)/(target_yield_strength)
        diff_ultimate_tensile_strength = abs(prop.ultimate_tensile_strength - target_ultimate_tensile_strength)/(target_ultimate_tensile_strength)
        diff_elastic_modulus = abs(prop.elastic_modulus - target_elastic_modulus)/(target_elastic_modulus)
        diff_thermal_conductivity = abs(prop.thermal_conductivity - target_thermal_conductivity) / (target_thermal_conductivity)
        diff_max_service_temp = abs(prop.max_service_temp - target_max_service_temp) / (target_max_service_temp)
        return diff_density + diff_yield_strength + diff_ultimate_tensile_strength + diff_elastic_modulus + diff_thermal_conductivity + diff_max_service_temp

    best_match = sorted(materials_list.items(), key = difference)
    print(f"Overall best match for target: ")
    print(f"""Density: {target_density} | 
          Yield Strength: {target_yield_strength} | 
          Ultimate Tensile Strength {target_ultimate_tensile_strength} | 
          Elastic Modulus: {target_elastic_modulus} | 
          Thermal Conductivity: {target_thermal_conductivity} | 
          Maximum Service Temperature: {target_max_service_temp} """ )
    
    print("="*50)
    for rank, (material, prop) in enumerate(best_match, 1):
        score = difference((material, prop))
        similarity = max(0.0, (1.0 - (score / 6.0)) * 100)
        print(f"{rank}. {material} ({similarity:.1f}% Match)")
        print(f"Density: {prop.density} g/cm^3")
        print(f"Yield Strength: {prop.yield_strength} MPa")
        print(f"Ultimate Tensile Strength: {prop.target_ultimate_tensile_strength} MPa")
        print(f"Elastic Modulus: {prop.elastic_modulus} GPa")
        print(f"Thermal Conductivity: {prop.thermal_conductivity} W/m-K")
        print(f"Maximum Service Temperature: {prop.max_service_temp} C")
        print("="*50)


while True:
    choice = input("Press (1) to view materials database, (2) to match ALL properties or (Q) to quit: ").strip().upper()

    if choice == "1":
        material_table()
    elif choice == "2":
        user_material()
    elif choice == "Q":
        print("Quitting program.")
        break
    else:
        print("Invalid choice. Please try again. ")