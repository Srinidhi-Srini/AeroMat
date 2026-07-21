import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import streamlit as st

st.set_page_config(page_title="AeroMat", layout="wide")
st.title("AeroMat — Aerospace Material Selection Tool")

# Loading materials databsae
df = pd.read_csv("materials.csv")
df["specific_strength"] = (df["yield_strength"] / df["density"]).round(1)
df["specific_stiffness"] = (df["elastic_modulus"] / df["density"]).round(1)

# Tabs replacing the while loop menu
tab1, tab2, tab3 = st.tabs(["Match by Target", "Filter & Rank", "Materials Database"])

# Sorts material by proximity to desired properties
with tab1:
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
        display_cols = ['name', 'density', 'yield_strength', 'ultimate_tensile_strength',
                        'elastic_modulus', 'thermal_conductivity', 'max_service_temp',
                        'specific_strength', 'specific_stiffness', 'similarity']
        st.dataframe(
            results1[display_cols].rename(columns={
                'name': 'Material',
                'family':'Family',
                'density': 'Density (g/cm³)',
                'yield_strength': 'Yield Str. (MPa)',
                'ultimate_tensile_strength': 'UTS (MPa)',
                'elastic_modulus': 'Elastic Modulus (GPa)',
                'thermal_conductivity': 'Thermal Cond. (W/m·K)',
                'max_service_temp': 'Max Service Temp. (°C)',
                'specific_strength': 'Sp. Strength',
                'specific_stiffness': 'Sp. Stiffness',
                'similarity': 'Similarity (%)'
            }).style.format({
                'Density (g/cm³)': '{:.1f}',
                'Elastic Modulus (GPa)': '{:.1f}',
                'Thermal Cond. (W/m·K)':'{:.1f}',
                'Similarity (%)': '{:.1f}',
                'Sp. Strength': '{:.1f}',
                'Sp. Stiffness': '{:.1f}'
            }),
            use_container_width=True, hide_index=True
        )

# Sorts materials by filtering based on desired quantity
with tab2:
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
 
        display_cols2 = ['name', 'density', 'yield_strength', 'ultimate_tensile_strength',
                        'elastic_modulus', 'thermal_conductivity', 'max_service_temp',
                        'specific_strength', 'specific_stiffness', 'score']
        st.dataframe(
            sorted_df2[display_cols2].rename(columns={
                'name': 'Material',
                'family': 'Family',
                'density': 'Density (g/cm³)',
                'yield_strength': 'Yield Str. (MPa)',
                'ultimate_tensile_strength': 'UTS (MPa)',
                'elastic_modulus': 'Elastic Modulus (GPa)',
                'thermal_conductivity': 'Thermal Cond. (W/m·K)',
                'max_service_temp': 'Max Service Temp. (°C)',
                'specific_strength': 'Sp. Strength',
                'specific_stiffness': 'Sp. Stiffness',
                'score': 'Score'
            }).style.format({
                'Score': '{:.3f}',
                'Density (g/cm³)': '{:.1f}',
                'Elastic Modulus (GPa)': '{:.1f}',
                'Thermal Cond. (W/m·K)':'{:.1f}',
                'Similarity (%)': '{:.1f}',
                'Sp. Strength': '{:.1f}',
                'Sp. Stiffness': '{:.1f}'
            }),
            use_container_width=True, hide_index=True
        )
 
    # Charts
    plt.style.use('seaborn-v0_8-whitegrid')

    figure, axes = plt.subplots(1, 2, figsize=(14, 6))
    figure.patch.set_facecolor('#0e1117')  # match Streamlit dark background

    for ax in axes:
        ax.set_facecolor('#0e1117')
        ax.tick_params(colors='white', labelsize=9)
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.title.set_color('white')
        for spine in ax.spines.values():
            spine.set_edgecolor('#333333')

    # Bar chart 
    colors = plt.cm.Blues(
    [0.4 + 0.6 * (i / max(len(sorted_df2) - 1, 1)) 
    for i in range(len(sorted_df2) - 1, -1, -1)]
    )
    bars = axes[0].barh(
        sorted_df2['name'],
        sorted_df2['score'],
        color=colors,
        edgecolor='none',
        height=0.6
        )
    
    axes[0].invert_yaxis()
    axes[0].set_title("Performance Score", fontsize=12, fontweight='bold', pad=12)
    axes[0].set_xlabel("Score (0–1)", fontsize=10)
    axes[0].set_xlim(0, 1.15)
    axes[0].grid(True, axis='x', alpha=0.15, color='white')
    axes[0].grid(False, axis='y')

    # Add score labels at end of each bar
    for bar, (_, row) in zip(bars, sorted_df2.iterrows()):
        axes[0].text(
            bar.get_width() + 0.02,
            bar.get_y() + bar.get_height() / 2,
            f"{row['score']:.3f}",
            va='center', ha='left',
            fontsize=8, color='white'
            )

    # Ashby chart
    # All materials — gray
    axes[1].scatter(
        df['density'], df[chosen_column],
        color='#555555', s=60, alpha=0.5, zorder=2
        )

    # Matched materials 
    scatter = axes[1].scatter(
        sorted_df2['density'], sorted_df2[chosen_column],
        c=sorted_df2['score'],
        cmap='Blues',
        vmin=0, vmax=1,
        s=150, alpha=0.95,
        edgecolors='white', linewidths=0.5,
        zorder=3
        )

    # Labels for matched materials only
    for _, row in sorted_df2.iterrows():
        axes[1].annotate(
            row['name'],
            (row['density'], row[chosen_column]),
            fontsize=7, ha='left',
            xytext=(7, 4), textcoords='offset points',
            color='white', fontweight='bold',
            bbox=dict(
                boxstyle='round,pad=0.2',
                facecolor='#1a1a2e',
                edgecolor='none',
                alpha=0.7
            )
        )

    axes[1].set_title(f"{ashby_prop} vs Density", fontsize=12, fontweight='bold', pad=12)
    axes[1].set_xlabel("Density (g/cm³)", fontsize=10)
    axes[1].set_ylabel(ashby_prop, fontsize=10)
    axes[1].grid(True, alpha=0.1, color='white')

    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#555555',
            markersize=7, alpha=0.5, label='All materials'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='steelblue',
            markersize=7, label='Matched materials')
    ]
    axes[1].legend(handles=legend_elements, fontsize=8,
                facecolor='#1a1a2e', edgecolor='#333333',
                labelcolor='white')

    plt.tight_layout(pad=2.0)
    st.pyplot(figure)
    plt.close(figure)
 
# Shows the materials database
with tab3:
    st.subheader("Materials Database")
    st.dataframe(df, use_container_width=True, hide_index=True)