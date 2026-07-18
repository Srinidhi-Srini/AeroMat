import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from typing import NamedTuple

class MaterialProp(NamedTuple):
    material: str
    density: float 
    yield_strength: float
    elastic_modulus: float

materials_list: dict[str, MaterialProp] = {
    "Ti-6Al-4V": MaterialProp(material="Ti-6Al-4V", density=4.429, yield_strength=880.0, elastic_modulus=104),
    "Al 7075": MaterialProp(material="Al 7075", density=2.81, yield_strength=572, elastic_modulus=72),
    "Stainless Steel 304": MaterialProp(material="Stainless Steel 304", density=7.9, yield_strength=215, elastic_modulus=190),
    "Hastelloy": MaterialProp(material="Hastelloy", density=8.9, yield_strength=355, elastic_modulus=205)
}

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

def user_density():
    try:
        user_density = float(input("Enter your desired density (in g/cm^3): "))
    except:
        print("Invalid input. Please enter a number.")
        return

    closest_density = sorted(materials_list.items(), key = lambda item:abs(item[1].density - user_density))

    print(f"The materials closest to your desired density of {user_density} g/cm^3: ")
    for material, (name, density, *_) in closest_density:
        print(f"{material}: {density}")

def user_yield_strength():
    try:
        user_yield_strength = float(input("Enter your desired yield strength (in MPa): "))
    except:
        print("Invalid input. Please enter a number.")
        return

    closest_yield_strength = sorted(materials_list.items(), key = lambda item:abs(item[1].yield_strength - user_yield_strength))
    print(f"The materials closest to your desired yield strength of {user_yield_strength} MPa: ")
    for material, (name, _, yield_strength, _) in closest_yield_strength:
        print(f"{material}: {yield_strength}")

def user_elastic_modulus():
    try: 
        user_elastic_modulus = float(input("Enter your desired elastic modulus (in GPa): "))
    except:
        print("Invalid input. Please enter a number.")
        return
    
    closest_elastic_modulus = sorted(materials_list.items(), key = lambda item: abs(item[1].elastic_modulus - user_elastic_modulus))
    print(f"The materials closest to your desired elastic modulus  of {user_elastic_modulus} GPa: ")
    for material, (name, _, _, elastic_modulus) in closest_elastic_modulus:
        print(f"{material}: {elastic_modulus}")

def user_material():
    try:
        target_density = float(input("Enter your desired density (in g/cm^3): "))
        target_yield_strength = float(input("Enter your desired yield strength (in MPa): "))
        target_elastic_modulus = float(input("Enter your desired elastic modulus (in GPa): "))
    except:
        print("Invalid input. Please enter a number.")
        return

    def difference(item):
        prop = item[1]
        diff_density = abs(prop.density - target_density)/(target_density)     
        diff_yield_strength = abs(prop.yield_strength - target_yield_strength)/(target_yield_strength)
        diff_elastic_modulus = abs(prop.elastic_modulus - target_elastic_modulus)/(target_elastic_modulus)
        return diff_density + diff_yield_strength + diff_elastic_modulus

    best_match = sorted(materials_list.items(), key = difference)
    print(f"Overall best match for target: ")
    print(f"Density: {target_density} | Yield Strength: {target_yield_strength} | Elastic Modulus: {target_elastic_modulus}" )
    print("="*25)
    for rank, (material, prop) in enumerate(best_match, 1):
        score = difference((material, prop))
        similarity = max(0.0, (1.0 - (score / 3.0)) * 100)
        print(f"{rank}. {material} ({similarity:.1f}% Match)")
        print(f"Density: {prop.density} g/cm^3")
        print(f"Yield Strength: {prop.yield_strength} MPa")
        print(f"Elastic Modulus: {prop.elastic_modulus} GPa")
        print("="*25)


while True:
    choice = input("Press (1) to sort by density, (2) to sort by yield strength, (3) to sort by elastic modulus, (4) to match ALL properties, or (Q) to quit: ").strip().upper()

    if choice == "1":
        user_density()
    elif choice == "2":
        user_yield_strength()
    elif choice == "3":
        user_elastic_modulus()
    elif choice == "4":
        user_material()
    elif choice == "Q":
        print("Quitting program.")
        break
    else:
        print("Invalid choice. Please try again. ")