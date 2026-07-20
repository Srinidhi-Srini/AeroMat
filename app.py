import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import streamlit as st

st.set_page_config(page_title="AeroMat", layout="wide")
st.title("AeroMat — Aerospace Material Selection Tool")

# Loading materials databsae
df = pd.read_csv("materials.csv")
df["specific_strength"] = df["yield_strength"] / df["density"].round(1)
df["specific_stiffness"] = df["elastic_modulus"] / df["density"].round(1)

# Tabs replacing the while loop menu
tab1, tab2, tab3 = st.tabs(["Materials Database", "Match by Target", "Filter & Rank"])

# Shows the materials database
with tab1:
    st.subheader("Materials Database")
    st.dataframe(df, use_container_width=True, hide_index=True)

# Sorts material by proximity to desired properties
with tab2:
    st.subheader("Match by Target Properties")
    st.caption("Find materials closest to your target values across density, yield strength, and service temperature.")
 
    col1, col2 = st.columns(2)
    with col1:
        target_density = st.number_input("Target Density (g/cm³)", min_value=0.1, max_value=20.0, value=4.0, step=0.1)
        target_yield_strength = st.number_input("Target Yield Strength (MPa)", min_value=0, max_value=2000, value=300, step=10)
    with col2:
        target_max_service_temp = st.number_input("Target Maximum Service Temp (°C)", min_value=0, max_value=1500, value=100, step=10)
        target_similarity = st.slider("Minimum Similarity Score (%)", min_value=0, max_value=100, value=50)
 
    def difference(row):
        diff_density = abs(row['density'] - target_density) / target_density
        diff_yield_strength = abs(row['yield_strength'] - target_yield_strength) / target_yield_strength
        diff_max_service_temp = abs(row['max_service_temp'] - target_max_service_temp) / target_max_service_temp
        return diff_density + diff_yield_strength + diff_max_service_temp
 
    scored_df = df.copy()
    scored_df['score'] = scored_df.apply(difference, axis=1)
    scored_df['similarity'] = scored_df['score'].apply(lambda s: max(0.0, (1.0 - (s / 3.0)) * 100))
    sorted_df1 = scored_df.sort_values(by='score', ascending=True)
    results1 = sorted_df1[sorted_df1['similarity'] >= target_similarity].copy()
 
    if results1.empty:
        st.warning("No materials found above your similarity threshold. Try lowering the minimum similarity score.")
    else:
        st.success(f"{len(results1)} material(s) found above {target_similarity}% similarity.")
        display_cols = ['material', 'density', 'yield_strength', 'ultimate_tensile_strength',
                        'elastic_modulus', 'thermal_conductivity', 'max_service_temp',
                        'specific_strength', 'specific_stiffness', 'similarity']
        st.dataframe(
            results1[display_cols].rename(columns={
                'material': 'Material',
                'density': 'Density (g/cm³)',
                'yield_strength': 'Yield Strength. (MPa)',
                'ultimate_tensile_strength': 'Ultimate Tensile Strength (MPa)',
                'elastic_modulus': 'Elastic Modulus (GPa)',
                'thermal_conductivity': 'Thermal Conductivity (W/m·K)',
                'max_service_temp': 'Maximum Service Temperature (°C)',
                'specific_strength': 'Specific Strength',
                'specific_stiffness': 'Specific Stiffness',
                'similarity': 'Similarity (%)'
            }).style.format({
                'Density (g/cm³)': '{:.1f}',
                'Elastic Modulus (GPa)': '{:.1f}',
                'Thermal Conductivity (W/m·K)':'{:.1f}',
                'Similarity (%)': '{:.1f}',
                'Specific Strength': '{:.1f}',
                'Specific Stiffness': '{:.1f}'
            }),
            use_container_width=True, hide_index=True
        )

# Sorts materials by filtering based on desired quantity
with tab3:
    st.subheader("Filter & Rank by Requirements")
    st.caption("Set minimum requirements and rank surviving materials by weighted performance score.")
 
    col1, col2 = st.columns(2)
    with col1:
        max_density = st.slider("Maximum Density (g/cm³)", 1.0, 10.0, 5.0, 0.1)
        min_yield_strength = st.slider("Minimum Yield Strength (MPa)", 0, 1500, 300, 25)
        min_service_temp = st.slider("Minimum Service Temperature (°C)", 0, 1000, 150, 25)
    with col2:
        st.markdown("**Scoring weights**")
        w_ss = st.slider("Specific Strength weight", 0, 10, 5)
        w_sk = st.slider("Specific Stiffness weight", 0, 10, 5)
        ashby_prop = st.selectbox("Ashby chart y-axis", [
            "Yield Strength (MPa)",
            "Ultimate Tensile Strength (MPa)",
            "Elastic Modulus (GPa)",
            "Thermal Conductivity (W/m·K)",
            "Max Service Temp (°C)",
            "Specific Strength",
            "Specific Stiffness"
        ])
 
    ashby_col_map = {
        "Yield Strength (MPa)": "yield_strength",
        "Ultimate Tensile Strength (MPa)": "ultimate_tensile_strength",
        "Elastic Modulus (GPa)": "elastic_modulus",
        "Thermal Conductivity (W/m·K)": "thermal_conductivity",
        "Max Service Temp (°C)": "max_service_temp",
        "Specific Strength": "specific_strength",
        "Specific Stiffness": "specific_stiffness"
    }
    chosen_column = ashby_col_map[ashby_prop]
 
    filtered_df = df[
        (df['density'] <= max_density) &
        (df['yield_strength'] >= min_yield_strength) &
        (df['max_service_temp'] >= min_service_temp)
    ].copy()
 
    if filtered_df.empty:
        st.warning("No materials match your requirements.")
    else:
        total_w = w_ss + w_sk or 1
        if len(filtered_df) == 1:
            filtered_df['score'] = 1.0
            sorted_df2 = filtered_df
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
                (filtered_df['norm_specific_strength'] * (w_ss / total_w)) +
                (filtered_df['norm_specific_stiffness'] * (w_sk / total_w))
            )
            sorted_df2 = filtered_df.sort_values(by='score', ascending=False)
 
        st.success(f"{len(filtered_df)} material(s) matched. Ranked by weighted performance score.")
 
        display_cols2 = ['material', 'density', 'yield_strength', 'max_service_temp',
                         'specific_strength', 'specific_stiffness', 'score']
        st.dataframe(
            sorted_df2[display_cols2].rename(columns={
                'material': 'Material',
                'density': 'Density (g/cm³)',
                'yield_strength': 'Yield Strength. (MPa)',
                'ultimate_tensile_strength': 'Ultimate Tensile Strength (MPa)',
                'elastic_modulus': 'Elastic Modulus (GPa)',
                'thermal_conductivity': 'Thermal Conductivity (W/m·K)',
                'max_service_temp': 'Maximum Service Temperature (°C)',
                'specific_strength': 'Specific Strength',
                'specific_stiffness': 'Specific Stiffness',
                'score': 'Score'
            }).style.format({
                'Score': '{:.3f}',
                'Density (g/cm³)': '{:.1f}',
                'Elastic Modulus (GPa)': '{:.1f}',
                'Thermal Conductivity (W/m·K)':'{:.1f}',
                'Similarity (%)': '{:.1f}',
                'Specific Strength': '{:.1f}',
                'Specific Stiffness': '{:.1f}'
            }),
            use_container_width=True, hide_index=True
        )
 
        # Charts
        figure, axes = plt.subplots(1, 2, figsize=(12, 5))
 
        # Bar chart
        axes[0].barh(sorted_df2['material'], sorted_df2['score'], color='steelblue')
        axes[0].invert_yaxis()
        axes[0].set_title("Matched Materials — Performance Score")
        axes[0].set_xlabel("Score (0–1)")
        axes[0].set_ylabel("Material")
        axes[0].set_xlim(0, 1)
 
        # Ashby chart
        axes[1].scatter(df['density'], df[chosen_column], color='grey', s=100, alpha=0.4)
        axes[1].scatter(sorted_df2['density'], sorted_df2[chosen_column], color='steelblue', s=120, alpha=0.8)
 
        for _, row in sorted_df2.iterrows():
            axes[1].annotate(
                row['material'],
                (row['density'], row[chosen_column]),
                fontsize=6, ha='left',
                xytext=(6, 3), textcoords='offset points',
                color='steelblue', fontweight='bold'
            )
 
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='steelblue', markersize=8, label='Matched'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='grey', markersize=8, alpha=0.4, label='All materials')
        ]
        axes[1].legend(handles=legend_elements, fontsize=8)
        axes[1].set_title(f"{ashby_prop} vs Density")
        axes[1].set_xlabel("Density (g/cm³)")
        axes[1].set_ylabel(ashby_prop)
        axes[1].grid(True, alpha=0.2)
 
        plt.tight_layout()
        st.pyplot(figure)
        plt.close(figure)
 