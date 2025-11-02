import pandas as pd
import geopandas as gpd
import folium
# We no longer need 'requests' or 'io'
# import requests
# import io

# --- 1. LOAD YOUR PRICE DATA ---
# Load the CSV file
try:
    price_df = pd.read_csv('housing_prices.csv')
except FileNotFoundError:
    print("Error: 'housing_prices.csv' not found.")
    print("Please make sure the CSV file is in the same directory as this script.")
    exit()

# Fill missing prices with 0, as requested
price_df['Price'] = price_df['Price'].fillna(0)

# --- 2. LOAD THE GEOJSON MAP DATA ---
# ** FIX: Load the map from the local file you uploaded. **
# This file should be in the same directory as this script.
local_geojson_file = 'limites-administratives-agglomeration-nad83.geojson'

try:
    # Read the local file
    gdf = gpd.read_file(local_geojson_file)

except Exception as e:
    print(f"Error: Could not read local GeoJSON file '{local_geojson_file}'.")
    print("Please make sure you have downloaded it and saved it in the correct directory.")
    print(f"Details: {e}")
    exit()


# --- 3. MERGE THE DATA ---
# This mapping helps match names between the GeoJSON (key) and your CSV (value)
# This is the same logic from the JavaScript file, just in Python
name_mapping = {
    # Names in the new GeoJSON are slightly different (hyphens vs. en-dashes)
    # but the keys will still match.
    "Côte-des-Neiges–Notre-Dame-de-Grâce": "Côte-des-Neiges",
    "Côte-des-Neiges-Notre-Dame-de-Grâce": "Côte-des-Neiges",
    "L'Île-Bizard–Sainte-Geneviève": "L'Ile-Bizard",
    "L'Île-Bizard-Sainte-Geneviève": "L'Ile-Bizard",
    "L'Île-Dorval": "L'Ile-Dorval",
    "Mercier–Hochelaga-Maisonneuve": "Mercier-Hochelaga-Maisonneuve",
    "Mercier-Hochelaga-Maisonneuve": "Mercier-Hochelaga-Maisonneuve",
    "Le Plateau-Mont-Royal": "Plateau-Mont-Royal",
    "Le Sud-Ouest": "Sud-Ouest"
}

# Create a new column in the GeoDataFrame with the names that match your CSV
# It first tries to map the name, and if it can't find a map, it uses the original name
# This GeoJSON file uses 'NOM' for the name property.
gdf['csv_name'] = gdf['NOM'].map(name_mapping).fillna(gdf['NOM'])

# Merge the GeoDataFrame (map) with the Pandas DataFrame (prices)
merged_gdf = gdf.merge(price_df, left_on='csv_name', right_on='Address', how='left')

# Fill in price for any map areas that weren't in your CSV
merged_gdf['Price'] = merged_gdf['Price'].fillna(0)


# --- 4. CREATE THE MAP ---

# ** FIX: Filter the GeoDataFrame to only include columns we need. **
# This prevents a TypeError because the 'DATEMODIF' column
# is read as a Timestamp, which is not JSON serializable by folium.
columns_to_keep = ['geometry', 'csv_name', 'Price', 'NOM']
merged_gdf = merged_gdf[columns_to_keep]

# Initialize the map, centered on Montreal, with the dark theme
m = folium.Map(location=[45.5017, -73.5673], zoom_start=10, tiles='CartoDB dark_matter')

# Define the price bins and colors (same as the JS version)
price_bins = [0, 250000, 500000, 750000, 1000000, max(merged_gdf['Price'].max(), 1000001)]
# Note: The 'colors' list is not directly used by this Choropleth, but
# 'threshold_scale' and 'fill_color' work together.
# colors = ['#999999', '#cbc9e2', '#9e9ac8', '#756bb1', '#54278f']


# Create the Choropleth layer
folium.Choropleth(
    geo_data=merged_gdf,
    name='Montreal Housing Prices',
    data=merged_gdf,
    columns=['csv_name', 'Price'], # Use the key and the value
    key_on='feature.properties.csv_name', # Link to the GeoJSON property

    # ** FIX: 'YlOrRd_09' is not a valid color code. Use 'YlOrRd'. **
    fill_color='YlOrRd', # A standard ColorBrewer color ramp

    # Custom threshold scale and colors
    threshold_scale=price_bins,
    fill_opacity=0.7,
    line_opacity=0.3,
    line_color='#444',
    legend_name='Housing Price ($)',
    highlight=True
).add_to(m)

# --- 5. ADD TOOLTIPS (for hover info) ---
# Add a GeoJson layer just for the tooltips
folium.GeoJson(
    merged_gdf,
    style_function=lambda x: {'fillOpacity': 0, 'weight': 0}, # Make this layer invisible
    tooltip=folium.GeoJsonTooltip(
        # This file uses 'NOM'
        fields=['NOM', 'Price'],
        aliases=['Municipality:', 'Price:'],
        localize=True,
        sticky=False,
        style="""
            background-color: #F0EFEF;
            border: 2px solid black;
            border-radius: 3px;
            box-shadow: 3px;
            color: #333;
            font-family: sans-serif;
            font-size: 14px;
        """
    ),
    highlight_function=lambda x: {'weight': 3, 'color': '#FFF', 'fillOpacity': 0.5} # Highlight from JS
).add_to(m)


# Add layer control to turn layers on/off
folium.LayerControl().add_to(m)

# --- 6. SAVE THE MAP ---
output_filename = 'montreal_map.html'
m.save(output_filename)

print(f"Success! Map has been saved to {output_filename}")

