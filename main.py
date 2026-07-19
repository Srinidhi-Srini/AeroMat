import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv("materials.csv")
df["specific_strength"] = df["yield_strength"] / df["density"]
df["specific_stiffness"] = df["elastic_modulus"] / df["density"]

def material_table():
    print(df.to_string())

def user_material_ver1():
    try:
        target_density = float(input("Enter your desired density (in g/cm^3): "))
        target_yield_strength = float(input("Enter your desired yield strength (in MPa): "))
        target_max_service_temp = float(input("Enter your desired maximum service temperature (C): "))
        target_similarity = float(input("Enter your desired minimum similarity score (1-100): "))
    except:
        print("Invalid input. Please enter a number.")
        return

    def difference(row):
        diff_density = abs(row['density'] - target_density) / target_density
        diff_yield_strength = abs(row['yield_strength'] - target_yield_strength) / target_yield_strength
        diff_max_service_temp = abs(row['max_service_temp'] - target_max_service_temp) / target_max_service_temp
        return diff_density + diff_yield_strength + diff_max_service_temp

    scored_df = df.copy()
    scored_df['score'] = scored_df.apply(difference, axis=1)
    sorted_df = scored_df.sort_values(by='score', ascending=True)

    print("="*50)
    print(f"Materials within {target_similarity:.1f}% similarity:")
    print(f"Target — Density: {target_density} | Yield Strength: {target_yield_strength} | Max Temp: {target_max_service_temp}")
    print("="*50)

    found = False
    for rank, (index, row) in enumerate(sorted_df.iterrows(), 1):
        similarity = max(0.0, (1.0 - (row['score'] / 3.0)) * 100)
        if similarity >= target_similarity:
            found = True
            print(f"{rank}. {row['material']} ({similarity:.1f}% Match)")
            print(f"Density: {row['density']} g/cm^3")
            print(f"Yield Strength: {row['yield_strength']} MPa")
            print(f"Ultimate Tensile Strength: {row['ultimate_tensile_strength']} MPa")
            print(f"Elastic Modulus: {row['elastic_modulus']} GPa")
            print(f"Thermal Conductivity: {row['thermal_conductivity']} W/m*K")
            print(f"Maximum Service Temperature: {row['max_service_temp']} C")
            print(f"Specific Strength: {row['specific_strength']:.1f} MPa·cm³/g")
            print(f"Specific Stiffness: {row['specific_stiffness']:.1f} GPa·cm³/g")
            print("="*50)
    
    if not found:
        print("No materials found above your similarity threshold.")
        print("Try lowering your minimum similarity score.")

def user_material_ver2():
    try:
        max_density = float(input("Enter your maximum density (in g/cm^3): "))
        min_yield_strength = float(input("Enter your minimum yield strength (in MPa): "))
        min_service_temp = float(input("Enter your minimum service temperature (C): "))
    except:
        print("Invalid input. Please enter a number.")
        return

    filtered_df = df[
        (df['density'] <= max_density) &
        (df['yield_strength'] >= min_yield_strength) &
        (df['max_service_temp'] >= min_service_temp)
    ].copy()

    if filtered_df.empty:
        print("No materials match your requirements.")
        print("Try relaxing your constraints.")
        return

    if len(filtered_df) == 1:
        filtered_df['score'] = 1.0
        sorted_df = filtered_df
    else:
        filtered_df['norm_specific_strength'] = (
            (filtered_df['specific_strength'] - filtered_df['specific_strength'].min()) /
            (filtered_df['specific_strength'].max() - filtered_df['specific_strength'].min())
        )
        filtered_df['norm_specific_stiffness'] = (
            (filtered_df['specific_stiffness'] - filtered_df['specific_stiffness'].min()) /
            (filtered_df['specific_stiffness'].max() - filtered_df['specific_stiffness'].min())
        )
        filtered_df['score'] = (
            (filtered_df['norm_specific_strength'] * 0.5) +
            (filtered_df['norm_specific_stiffness'] * 0.5)
        )
        sorted_df = filtered_df.sort_values(by='score', ascending=False)

    print("="*50)
    print(f"Materials matching your requirements:")
    print(f"Max Density: {max_density} g/cm^3 | Min Yield Strength: {min_yield_strength} MPa | Min Service Temp: {min_service_temp} C")
    print(f"{len(filtered_df)} material(s) found, ranked by performance score.")
    print("="*50)

    for rank, (index, row) in enumerate(sorted_df.iterrows(), 1):
        print(f"{rank}. {row['material']} (Score: {row['score']:.3f})")
        print(f"Density: {row['density']} g/cm^3")
        print(f"Yield Strength: {row['yield_strength']} MPa")
        print(f"Ultimate Tensile Strength: {row['ultimate_tensile_strength']} MPa")
        print(f"Elastic Modulus: {row['elastic_modulus']} GPa")
        print(f"Thermal Conductivity: {row['thermal_conductivity']} W/m*K")
        print(f"Maximum Service Temperature: {row['max_service_temp']} C")
        print(f"Specific Strength: {row['specific_strength']:.1f} MPa·cm^3/g")
        print(f"Specific Stiffness: {row['specific_stiffness']:.1f} GPa·cm^3/g")
        print("="*50)

while True:
    print("\nAeroMat - Aerospace Material Selection Tool")
    choice = input("(1) View full database  (2) Match by target values  (3) Filter by requirements  (Q) Quit: ").strip().upper()

    if choice == "1":
        material_table()
    elif choice == "2":
        user_material_ver1()
    elif choice == "3":
        user_material_ver2()
    elif choice == "Q":
        print("Quitting AeroMat.")
        break
    else:
        print("Invalid choice. Please try again.")