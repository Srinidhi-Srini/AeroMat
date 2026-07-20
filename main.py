import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import streamlit as st

st.set_page_config(page_title="AeroMat", layout="wide")
st.title("AeroMat — Aerospace Material Selection Tool")

# Loading materials databsae
df = pd.read_csv("materials.csv")
df["specific_strength"] = df["yield_strength"] / df["density"]
df["specific_stiffness"] = df["elastic_modulus"] / df["density"]

# Function that shows the materials database
def material_table():
    print(df.to_string())

# Function that sorts material by proximity to desired properties
def user_material_ver1():
    # Takes user input
    try:
        target_density = float(input("Enter your desired density (in g/cm^3): "))
        target_yield_strength = float(input("Enter your desired yield strength (in MPa): "))
        target_max_service_temp = float(input("Enter your desired maximum service temperature (C): "))
        target_similarity = float(input("Enter your desired minimum similarity score (1-100): "))
    except:
        print("Invalid input. Please enter a number.")
        return

    # calculates the absolute value of differences and then returns the sum for a score
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
    
    # prints the properties of each material that matches the conditions
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

# Function that sorts material by filtering based on desired quantity
def user_material_ver2():
    
    # takes user inputs
    try:
        max_density = float(input("Enter your desired maximum density (in g/cm^3): "))
        min_yield_strength = float(input("Enter your desired minimum yield strength (in MPa): "))
        min_service_temp = float(input("Enter your desired minimum service temperature (C): "))
        print("Available y-axis properties for ashby chart:\n(1) Yield Strength\n(2) Ultimate Tensile Strength \n(3) Elastic Modulus\n(4) Thermal Conductivity \n(5) Maximum Service Temperature\n(6) Specific Strength\n(7) Specific Stiffness")
        ashby = input("Select y-axis property # (x-axis is preset to density): ").strip()

    except:
        print("Invalid input. Please enter a number.")
        return

    # filters it based off of min and max of user input
    filtered_df = df[
        (df['density'] <= max_density) &
        (df['yield_strength'] >= min_yield_strength) &
        (df['max_service_temp'] >= min_service_temp)
    ].copy()

    if filtered_df.empty:
        print("No materials match your requirements.")
        print("Try relaxing your constraints.")
        return

    # normalizes quantities and returns score between 0 to 1
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
    
    # sets y-axis for ashby sale
    if ashby == "1":
        ashby_type = "Yield Strength (MPa)"
        ashby_y1 = sorted_df['yield_strength']      
        ashby_y2 = df['yield_strength']              
    elif ashby == "2":
        ashby_type = "Ultimate Tensile Strength (MPa)"
        ashby_y1 = sorted_df['ultimate_tensile_strength']
        ashby_y2 = df['ultimate_tensile_strength']
    elif ashby == "3":
        ashby_type = "Elastic Modulus (GPa)"
        ashby_y1 = sorted_df['elastic_modulus']
        ashby_y2 = df['elastic_modulus']
    elif ashby == "4":
        ashby_type = "Thermal Conductivity (W/m*K)"
        ashby_y1 = sorted_df['thermal_conductivity']
        ashby_y2 = df['thermal_conductivity']
    elif ashby == "5":
        ashby_type = "Maximum Service Temperature (C)"
        ashby_y1 = sorted_df['max_service_temp']
        ashby_y2 = df['max_service_temp']
    elif ashby == "6":
        ashby_type = "Specific Strength (MPa·cm³/g)"
        ashby_y1 = sorted_df['specific_strength']
        ashby_y2 = df['specific_strength']
    elif ashby == "7":
        ashby_type = "Specific Stiffness (GPa·cm³/g)"
        ashby_y1 = sorted_df['specific_stiffness']
        ashby_y2 = df['specific_stiffness']

    # prints materials that match
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

    
    # Bar chart showing matched materials and their ranking
    # Ashby chart that compares properties of different materials
    def charts():
        figure, axes = plt.subplots(1,2, figsize=(12,5))

        materials = sorted_df['material']
        score = sorted_df['score']
        axes[0].barh(materials, score)
        axes[0].invert_yaxis() 
        axes[0].set_title("Matched Materials & Scores")
        axes[0].set_xlabel("Score (0-1)")
        axes[0].set_ylabel("Material")
    
        x_axis_1 = sorted_df['density']
        x_axis_2 = df['density']
        y_axis_1 = ashby_y1
        y_axis_2 = ashby_y2
        axes[1].scatter(x_axis_2, y_axis_2, color="grey", s=100, alpha = 0.6)
        axes[1].scatter(x_axis_1, y_axis_1, color="blue", s=100, alpha=0.6)
        axes[1].set_title(f"{ashby_type} - Density (g/cm^3)")
        axes[1].set_xlabel('Density (g/cm^3)')
        axes[1].set_ylabel(ashby_type)
        
        chosen_column = y_axis_2.name

        scatter_all = axes[1].scatter(x_axis_2, y_axis_2, color="grey", s=100, alpha=0.4)

        for _, row in sorted_df.iterrows():
            axes[1].annotate(
            row['material'],
            (row['density'], row[chosen_column]),
            fontsize=6,
            ha='left',
            xytext=(8, 4),
            textcoords='offset points',
            color='blue'
            )
        
        for _, row in df.iterrows():
            axes[1].annotate(
            row['material'],
            (row['density'], row[chosen_column]),
            fontsize=6,
            ha='left',
            xytext=(8, 4),
            textcoords='offset points',
            color='grey'
            )
        
        legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, alpha=0.8, label='Matched Materials'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='grey', markersize=8, alpha=0.4, label='All Materials')
        ]
        axes[1].legend(handles=legend_elements, loc='upper right', fontsize=8)

        plt.tight_layout()
        plt.show()

    charts()

# Main menu
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