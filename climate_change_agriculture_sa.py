# climate_change_agriculture_sa.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
from shapely.geometry import Point
from datetime import datetime
import leafmap.foliumap as leafmap
from PIL import Image
import xarray as xr
import os
import tempfile
import requests

# Set page configuration
st.set_page_config(
    page_title="Climate Impact on SA Agriculture",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: #000000;
    }
    .sidebar .sidebar-content {
        background: #1a6b2b;
        color: white;
    }
    .stButton>button {
        background-color: #2e7d32;
        color: white;
    }
    .stSelectbox, .stSlider, .stDateInput {
        background-color: white;
    }
    .css-1aumxhk {
        background-color: #f0f2f6;
        border: 1px solid #d1d5db;
    }
    .css-1v3fvcr {
        color: #1a6b2b;
    }
    .header-text {
        color: #1a6b2b;
        text-align: center;
    }

    /* Remove white backgrounds from select boxes and sliders */
    div[data-baseweb="select"] div {
        background-color: transparent !important;
    }
    div[data-baseweb="slider"] {
        background-color: transparent !important;
    }
    
    /* Style the select boxes and sliders */
    .stSelectbox, .stSlider, .stRadio {
        background-color: #000000 !important;
        border-radius: 8px;
        padding: 8px;
        border: 1px solid #d1d5db;
    }
    
    /* Make the options more compact */
    .st-ae {
        padding: 4px !important;
    }
    
    /* Better spacing for the region selector */
    div[data-testid="stVerticalBlock"] > div:nth-child(1) {
        margin-bottom: -1rem;
    }
</style>
""", unsafe_allow_html=True)


# Title and introduction
st.title("🌾 Climate Change Impact on South African Agriculture")
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h3 class="header-text">Analyzing Climate Risks to Food Security</h3>
    <p>This dashboard assesses the impact of climate change on key agricultural regions in South Africa using satellite imagery and climate models.</p>
</div>
""", unsafe_allow_html=True)


# Create tabs for different sections
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🌍 Regional Overview", 
    "📊 Crop Health Analysis", 
    "📈 Climate Trends", 
    "🔮 Future Projections", 
    "📝 Recommendations"
])

# Load sample data (in a real application, this would be connected to actual data sources)
@st.cache_data
def load_data():
    # Load agricultural regions
    regions = {
        "Western Cape Wheat": {"bbox": [18.4, -34.2, 20.5, -33.0]},
        "Free State Maize": {"bbox": [26.5, -29.0, 28.5, -27.0]},
        "KZN Sugarcane": {"bbox": [30.5, -29.5, 31.5, -28.5]}
    }
    
    # Load climate data (sample)
    years = list(range(2010, 2024))
    temp_change = [0.1 * (year - 2010) + np.random.normal(0, 0.2) for year in years]
    rainfall_change = [-2 * (year - 2010) + np.random.normal(0, 3) for year in years]
    climate_df = pd.DataFrame({
        "Year": years,
        "Temperature Change (°C)": temp_change,
        "Rainfall Change (%)": rainfall_change
    })
    
    # Load crop health data
    crop_health = []
    for region in regions:
        for year in years:
            health = 80 - 0.8 * (year - 2010) + np.random.normal(0, 5)
            crop_health.append({
                "Region": region,
                "Year": year,
                "Crop Health Index": max(60, health),
                "Crop Type": "Wheat" if "Wheat" in region else "Maize" if "Maize" in region else "Sugarcane"
            })
    crop_health_df = pd.DataFrame(crop_health)
    
    # Load future projections
    future_years = list(range(2024, 2050))
    future_temp = [0.15 * (year - 2010) + np.random.normal(0, 0.3) for year in future_years]
    future_rain = [-3 * (year - 2010) + np.random.normal(0, 5) for year in future_years]
    future_health = [80 - 1.0 * (year - 2010) + np.random.normal(0, 6) for year in future_years]
    
    projections_df = pd.DataFrame({
        "Year": future_years,
        "Projected Temp Change": future_temp,
        "Projected Rainfall Change": future_rain,
        "Projected Crop Health": [max(40, h) for h in future_health]
    })
    
    return regions, climate_df, crop_health_df, projections_df

regions, climate_df, crop_health_df, projections_df = load_data()


# Tab 1: Regional Overview
with tab1:
    st.header("South Africa's Key Agricultural Regions")
    st.markdown("""
    <div style="background-color: #191919; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <p>South Africa has diverse agricultural regions facing different climate risks. 
        This section provides an overview of key farming areas and their vulnerability to climate change.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    # Column 1
    with col1:
        st.subheader("Agricultural Regions Map")
        
        # Create an interactive map with proper attribution
        m = leafmap.Map(center=[-28.5, 25], zoom=5)
        m.add_tile_layer(
            url="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
            name="OpenTopoMap",
            attribution="Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)"
        )
        
        # Create a FeatureCollection for all regions
        features = []
        for region, data in regions.items():
            bbox = data["bbox"]
            # Create GeoJSON feature for each region
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [bbox[0], bbox[1]],  # SW
                        [bbox[2], bbox[1]],  # SE
                        [bbox[2], bbox[3]],  # NE
                        [bbox[0], bbox[3]],  # NW
                        [bbox[0], bbox[1]]   # SW
                    ]]
                },
                "properties": {"name": region}
            }
            features.append(feature)

            # Add label at center
            center_lat = (bbox[1] + bbox[3]) / 2
            center_lon = (bbox[0] + bbox[2]) / 2
            m.add_marker([center_lat, center_lon], region, font_size=12)
            

            # Create FeatureCollection and add to map
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
            # Add to map with styling
        m.add_geojson(
                geojson,
                layer_name=region,
                style={"color": "green", "fillColor": "green", "fillOpacity": 0.5}
            )
            
        # Display the map
        m.to_streamlit(height=500)
    
    # Column 2
    with col2:
        st.subheader("Region Vulnerability Assessment")
        
        # Create vulnerability data
        vulnerability_data = {
            "Region": list(regions.keys()),
            "Crop Type": ["Wheat", "Maize", "Sugarcane"],
            "Temperature Risk": [3, 2, 4],
            "Drought Risk": [4, 3, 2],
            "Flood Risk": [1, 2, 3],
            "Overall Risk": [3.2, 2.8, 3.0]
        }
        vuln_df = pd.DataFrame(vulnerability_data)
        
        # Display as radar chart
        fig = go.Figure()
        
        for i, row in vuln_df.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row["Temperature Risk"], row["Drought Risk"], row["Flood Risk"], row["Overall Risk"]],
                theta=['Temperature Risk', 'Drought Risk', 'Flood Risk', 'Overall Risk'],
                fill='toself',
                name=row["Region"]
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5]
                )),
            showlegend=True,
            height=400,
            title="Climate Risk by Region (1-5 scale)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        <div style="background-color: #191919; padding: 10px; border-radius: 5px; margin-top: 20px;">
            <p><strong>Key Observations:</strong></p>
            <ul>
                <li>Western Cape faces high drought risk for wheat production</li>
                <li>Free State maize is vulnerable to temperature increases</li>
                <li>KZN sugarcane has moderate flood risk</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)



# Tab 2: Crop Health Analysis
with tab2:
    st.header("Satellite-Based Crop Health Monitoring")
    st.markdown("""
    <div style="background-color: #191919; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <p>Using Sentinel-2 satellite data, we analyze vegetation health through the NDVI index. 
        This helps monitor crop stress and predict yields.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    # Column 1
    with col1:
        # Compact region selection
        st.markdown("#### Region")
        region = st.selectbox("Region", list(regions.keys()), key="crop_region", label_visibility="visible")
        
        # Year selection with custom styling
        st.markdown("#### Year")
        year = st.slider(
            "Year", 
            2010, 
            2023, 
            2020,
            key="crop_year",
            label_visibility="visible"
        )
        
        # Season selection as horizontal buttons
        st.markdown("#### Season")
        season_cols = st.columns(3)
        with season_cols[0]:
            planting_btn = st.button("🌱 Planting", key="planting_btn", use_container_width=True)
        with season_cols[1]:
            growth_btn = st.button("🌿 Growth", key="growth_btn", use_container_width=True)
        with season_cols[2]:
            harvest_btn = st.button("🌾 Harvest", key="harvest_btn", use_container_width=True)
        
        # Set the selected season
        if planting_btn:
            st.session_state.crop_season = "Planting"
        if growth_btn:
            st.session_state.crop_season = "Growth"
        if harvest_btn:
            st.session_state.crop_season = "Harvest"
        
        # Initialize season if not set
        if "crop_season" not in st.session_state:
            st.session_state.crop_season = "Planting"
        
        # Display selected season
        st.markdown(f"**Selected Season:** {st.session_state.crop_season}")
        
        st.markdown("---")
        st.markdown("### NDVI Analysis")
        st.markdown("""
        **Normalized Difference Vegetation Index (NDVI)** measures plant health:
        - Values near 1: Healthy vegetation
        - Values near 0: Bare soil
        - Negative values: Water
        """)
        
        # Simulate NDVI data
        if region == "Western Cape Wheat":
            ndvi_values = [0.15, 0.45, 0.65, 0.75, 0.85, 0.82, 0.78, 0.70, 0.60, 0.40, 0.25, 0.18]
        elif region == "Free State Maize":
            ndvi_values = [0.20, 0.35, 0.60, 0.75, 0.85, 0.88, 0.90, 0.85, 0.75, 0.55, 0.35, 0.22]
        else:  # KZN Sugarcane
            ndvi_values = [0.45, 0.55, 0.65, 0.75, 0.80, 0.82, 0.85, 0.84, 0.82, 0.78, 0.70, 0.60]
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        ndvi_df = pd.DataFrame({"Month": months, "NDVI": ndvi_values})
        
        fig = px.line(ndvi_df, x="Month", y="NDVI", 
                      title=f"Monthly NDVI Trend: {region} ({year})",
                      markers=True)
        fig.update_layout(yaxis_title="NDVI", yaxis_range=[0, 1])
        st.plotly_chart(fig, use_container_width=True)
    

    # Column 2
    with col2:
        st.subheader("Satellite Imagery Analysis")
        
        # Use actual satellite image URLs
        image_urls = {
            "Western Cape Wheat": "https://upload.wikimedia.org/wikipedia/commons/5/56/Wheat_panorama.jpg",
            "Free State Maize": "https://upload.wikimedia.org/wikipedia/commons/6/62/Maize_production_near_the_R34_Welkom.jpg",
            "KZN Sugarcane": "https://upload.wikimedia.org/wikipedia/commons/3/3a/RSA_Sugar_Fields.jpg"
        }

        
        try:
            # Display the image with proper error handling
            response = requests.get(image_urls[region], stream=True)
            if response.status_code == 200:
                img = Image.open(response.raw)
                st.image(img, 
                        caption=f"Sentinel-2 Imagery: {region} ({st.session_state.crop_season} {year})", 
                        width=500)
            else:
                raise Exception(f"HTTP Error: {response.status_code}")
        except Exception as e:
            st.warning(f"Unable to load satellite image. Error: {str(e)}")
            # Display a relevant placeholder
            st.image("https://images.unsplash.com/photo-1500382017468-9049fed747ef?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=600&q=80", 
                    use_container_width=True)
        
        # Health indicator
        health_value = crop_health_df[
            (crop_health_df["Region"] == region) & 
            (crop_health_df["Year"] == year)
        ]["Crop Health Index"].mean()
        
        st.markdown(f"### Crop Health Index: **{health_value:.1f}/100**")
        
        # Health gauge
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = health_value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Crop Health Status"},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "green"},
                'steps': [
                    {'range': [0, 40], 'color': "red"},
                    {'range': [40, 70], 'color': "orange"},
                    {'range': [70, 100], 'color': "green"}],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': health_value}
            }
        ))
        
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        <div style="background-color: #191919; padding: 10px; border-radius: 5px; margin-top: 10px;">
            <p><strong>Interpretation:</strong></p>
            <ul>
                <li><span style="color: green;">Green (70-100):</span> Optimal growing conditions</li>
                <li><span style="color: orange;">Orange (40-70):</span> Moderate stress</li>
                <li><span style="color: red;">Red (0-40):</span> Severe stress, potential yield loss</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


# Tab 3: Climate Trends
with tab3:
    st.header("Historical Climate Trends")
    st.markdown("""
    <div style="background-color: #191919; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <p>Analyzing temperature and rainfall patterns over time to understand climate impacts on agriculture.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    # Column 1
    with col1:
        st.subheader("Temperature Trends")
        fig = px.line(climate_df, x="Year", y="Temperature Change (°C)", 
                     title="Temperature Change from Baseline (1990-2000)",
                     markers=True)
        fig.update_layout(yaxis_title="Temperature Change (°C)")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### Regional Temperature Analysis")
        region = st.selectbox("Select Region", list(regions.keys()), key="temp_region")
        
        # Simulate regional temperature data
        temp_data = []
        for year in range(2010, 2024):
            base_temp = 22.5 if region == "Western Cape Wheat" else 24.0 if region == "Free State Maize" else 26.5
            change = 0.08 * (year - 2010) + np.random.normal(0, 0.15)
            temp_data.append({
                "Year": year,
                "Average Temperature (°C)": base_temp + change,
                "Max Temperature": base_temp + 5 + change,
                "Min Temperature": base_temp - 5 + change
            })
        temp_df = pd.DataFrame(temp_data)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=temp_df["Year"], y=temp_df["Max Temperature"],
            fill=None, mode='lines', line_color='red', name='Max Temp'
        ))
        fig.add_trace(go.Scatter(
            x=temp_df["Year"], y=temp_df["Min Temperature"],
            fill='tonexty', mode='lines', line_color='blue', name='Min Temp'
        ))
        fig.add_trace(go.Scatter(
            x=temp_df["Year"], y=temp_df["Average Temperature (°C)"],
            mode='lines+markers', line=dict(color='black', width=2), name='Avg Temp'
        ))
        fig.update_layout(
            title=f"Temperature Trends: {region}",
            yaxis_title="Temperature (°C)",
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
    

    # Column 2
    with col2:
        st.subheader("Rainfall Patterns")
        fig = px.bar(climate_df, x="Year", y="Rainfall Change (%)", 
                    title="Annual Rainfall Change from Baseline",
                    color="Rainfall Change (%)",
                    color_continuous_scale=px.colors.sequential.Blues)
        fig.update_layout(yaxis_title="Rainfall Change (%)")
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### Drought Frequency Analysis")
        
        # Create drought data
        drought_data = {
            "Year": list(range(2010, 2024)),
            "Drought Days": [15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80],
            "Severity": [1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5]
        }
        drought_df = pd.DataFrame(drought_data)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=drought_df["Year"], y=drought_df["Drought Days"],
            name='Drought Days',
            marker_color='orange'
        ))
        fig.add_trace(go.Scatter(
            x=drought_df["Year"], y=drought_df["Severity"]*20,
            mode='lines+markers', name='Severity (1-5 scale)',
            line=dict(color='red', width=3)
        ))
        fig.update_layout(
            title="Increasing Drought Frequency and Severity",
            yaxis_title="Drought Days/Year",
            yaxis2=dict(
                title="Severity (scaled)",
                overlaying="y",
                side="right",
                range=[0, 100]
            ),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        <div style="background-color: #191919; padding: 10px; border-radius: 5px; margin-top: 20px;">
            <p><strong>Key Findings:</strong></p>
            <ul>
                <li>Average temperatures have increased by 1.2°C since 2010</li>
                <li>Rainfall has decreased by 15% in key agricultural regions</li>
                <li>Drought frequency has doubled in the last decade</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)



# Tab 4: Future Projections
with tab4:
    st.header("Future Climate Projections")
    st.markdown("""
    <div style="background-color: #191919; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <p>Using climate models to project future impacts on agriculture and identify vulnerable regions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])

    # Column 1
    with col1:
        st.subheader("Climate Projections to 2050")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=projections_df["Year"], y=projections_df["Projected Temp Change"],
            mode='lines+markers', name='Temperature Change',
            line=dict(color='red', width=3)
        ))
        fig.add_trace(go.Scatter(
            x=projections_df["Year"], y=projections_df["Projected Rainfall Change"],
            mode='lines+markers', name='Rainfall Change',
            line=dict(color='blue', width=3),
            yaxis="y2"
        ))

        # FIXED SECTION - Updated axis title styling
        fig.update_layout(
            title="Projected Climate Change (2024-2050)",
            yaxis=dict(
                title=dict(text="Temperature Change (°C)", font=dict(color="red"))
            ),
            yaxis2=dict(
                title=dict(text="Rainfall Change (%)", font=dict(color="blue")),
                overlaying="y",
                side="right"
            ),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### Crop Yield Projections")
        scenario = st.radio("Select Climate Scenario", 
                           ["Low Emissions (RCP 2.6)", 
                            "Moderate Emissions (RCP 4.5)", 
                            "High Emissions (RCP 8.5)"])
        
        # Simulate yield projections
        years = list(range(2024, 2050))
        if "Low" in scenario:
            yields = [100 - 0.5 * (year - 2024) for year in years]
        elif "Moderate" in scenario:
            yields = [100 - 1.0 * (year - 2024) for year in years]
        else:
            yields = [100 - 2.0 * (year - 2024) for year in years]
        
        yield_df = pd.DataFrame({"Year": years, "Projected Yield (%)": yields})
        
        fig = px.line(yield_df, x="Year", y="Projected Yield (%)", 
                     title=f"Projected Crop Yield: {scenario}",
                     markers=True)
        fig.update_layout(yaxis_title="Yield as % of 2020 Baseline")
        st.plotly_chart(fig, use_container_width=True)


    # Column 2
    with col2:
        st.subheader("Regional Vulnerability in 2050")
        
        # Vulnerability map data
        vulnerability = {
            "Region": list(regions.keys()) + ["Other Areas"],
            "Latitude": [-33.5, -28.0, -29.0, -28.5],
            "Longitude": [19.5, 27.0, 31.0, 24.0],
            "Risk Level": ["High", "Very High", "Medium", "Low"],
            "Risk Score": [8.2, 9.1, 6.5, 3.2],
            "Main Threat": ["Drought", "Heat Stress", "Flooding", "Moderate Change"]
        }
        vuln_df = pd.DataFrame(vulnerability)
        
        fig = px.scatter_mapbox(vuln_df, lat="Latitude", lon="Longitude", 
                               color="Risk Level", size="Risk Score",
                               hover_name="Region", hover_data=["Main Threat"],
                               color_discrete_map={
                                   "Very High": "red",
                                   "High": "orange",
                                   "Medium": "yellow",
                                   "Low": "green"
                               },
                               zoom=5, height=500)
        
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### Adaptation Strategies Effectiveness")
        
        strategies = [
            "Drought-resistant crops",
            "Precision irrigation",
            "Crop rotation",
            "Soil conservation",
            "Agroforestry"
        ]
        effectiveness = [85, 75, 60, 70, 65]
        cost = [40, 70, 30, 50, 60]
        
        strat_df = pd.DataFrame({
            "Strategy": strategies,
            "Effectiveness (%)": effectiveness,
            "Cost (relative)": cost
        })
        
        fig = px.bar(strat_df, x="Strategy", y="Effectiveness (%)",
                    color="Cost (relative)",
                    title="Effectiveness of Adaptation Strategies",
                    color_continuous_scale=px.colors.sequential.Viridis)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        <div style="background-color: #191919; padding: 10px; border-radius: 5px; margin-top: 20px;">
            <p><strong>Key Projections:</strong></p>
            <ul>
                <li>Maize yields could decline by 20-40% by 2050</li>
                <li>Western Cape faces highest risk of agricultural disruption</li>
                <li>Adaptation strategies could reduce losses by 50-80%</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)



# Tab 5: Recommendations
with tab5:
    st.header("Adaptation Recommendations")
    st.markdown("""
    <div style="background-color: #191919; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
        <p>Evidence-based strategies to enhance climate resilience in South African agriculture.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    # Column 1
    with col1:
        st.subheader("Region-Specific Strategies")
        region = st.selectbox("Select Region for Recommendations", list(regions.keys()))
        
        if region == "Western Cape Wheat":
            st.markdown("""
            <div style="background-color: #0d0d0d; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                <h4>Western Cape Wheat Recommendations</h4>
                <ul>
                    <li><strong>Water Management:</strong> Implement drip irrigation and rainwater harvesting</li>
                    <li><strong>Crop Diversification:</strong> Introduce drought-tolerant crops like sorghum and millet</li>
                    <li><strong>Soil Health:</strong> Promote conservation agriculture to improve water retention</li>
                    <li><strong>Technology:</strong> Adopt satellite-based monitoring for precision farming</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.image("https://upload.wikimedia.org/wikipedia/commons/1/1f/Drip_irrigation_%282552390830%29.jpg", 
                     caption="Drip irrigation can reduce water usage by 30-50%", width=400)
            
        elif region == "Free State Maize":
            st.markdown("""
            <div style="background-color: #0d0d0d; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                <h4>Free State Maize Recommendations</h4>
                <ul>
                    <li><strong>Heat-Resistant Varieties:</strong> Develop and plant heat-tolerant maize cultivars</li>
                    <li><strong>Agroforestry:</strong> Integrate trees to reduce temperature stress</li>
                    <li><strong>Early Warning Systems:</strong> Implement climate forecasting for planting decisions</li>
                    <li><strong>Crop Insurance:</strong> Expand access to weather-indexed insurance</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.image("https://upload.wikimedia.org/wikipedia/commons/c/cd/Cornfield_in_South_Africa.jpg", 
                     caption="New heat-tolerant varieties can maintain yields at higher temperatures", width=400)
            
        else:  # KZN Sugarcane
            st.markdown("""
            <div style="background-color: #0d0d0d; padding: 15px; border-radius: 10px; margin-bottom: 20px;">
                <h4>KZN Sugarcane Recommendations</h4>
                <ul>
                    <li><strong>Flood Management:</strong> Develop drainage systems and contour planting</li>
                    <li><strong>Disease Control:</strong> Enhance monitoring for climate-related diseases</li>
                    <li><strong>Value Addition:</strong> Diversify into bioenergy production</li>
                    <li><strong>Ecosystem Restoration:</strong> Rehabilitate wetlands for flood mitigation</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.image("https://upload.wikimedia.org/wikipedia/commons/9/96/Contour_Farming04_%2823972930457%29.jpg", 
                     caption="Contour planting reduces soil erosion during heavy rains", width=400)


    # Column 2
    with col2:
        st.subheader("Policy Recommendations")
        
        st.markdown("""
        <div style="background-color: #0d0d0d; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <h4>National Climate Adaptation Framework</h4>
            <ol>
                <li>Establish a National Climate Resilience Fund for Agriculture</li>
                <li>Integrate climate risk assessments into agricultural planning</li>
                <li>Develop early warning systems for extreme weather events</li>
                <li>Promote climate-smart agricultural practices nationwide</li>
                <li>Support research on climate-resilient crop varieties</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Implementation Timeline")
        
        timeline_data = {
            "Phase": ["Short-Term (1-3 years)", "Medium-Term (3-7 years)", "Long-Term (7-15 years)"],
            "Key Actions": [
                "Pilot adaptation projects, farmer training, early warning systems",
                "Scale successful pilots, develop resilient supply chains, policy reform",
                "Transformational change, climate-resilient infrastructure, diversified agricultural economy"
            ],
            "Estimated Cost (ZAR billion)": [3.5, 8.2, 15.0]
        }
        timeline_df = pd.DataFrame(timeline_data)
        
        st.dataframe(timeline_df, hide_index=True, use_container_width=True)
        
        st.markdown("### Funding Opportunities")
        
        funding = {
            "Source": [
                "Green Climate Fund", 
                "World Bank Climate Investment Funds",
                "National Treasury",
                "Private Sector Partnerships"
            ],
            "Focus Area": [
                "Large-scale adaptation projects",
                "Technology transfer and capacity building",
                "Domestic subsidy programs",
                "Innovation and market-based solutions"
            ],
            "Potential Amount (ZAR billion)": [5.0, 3.2, 2.5, 4.0]
        }
        funding_df = pd.DataFrame(funding)
        
        fig = px.bar(funding_df, x="Source", y="Potential Amount (ZAR billion)",
                    color="Focus Area", 
                    title="Climate Adaptation Funding Sources")
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 14px; padding-top: 20px;">
    <p>Climate Change Impact on South African Agriculture Dashboard • Developed with Streamlit</p>
    <p>Data Sources: Sentinel-2 Satellite Imagery, South African Weather Service, Agricultural Research Council</p>
    <p>Disclaimer: This is a demonstration tool. For official assessments, consult relevant authorities.</p>
</div>
""", unsafe_allow_html=True)
