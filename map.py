import pandas as pd
import geopandas as gpd
import folium
import csv
from branca.element import Element # Required for injecting custom JS

from housing_model import train_evaluate_and_predict


# --- 1. LOAD AND PRE-PROCESS YOUR PRICE DATA ---
input_csv = 'housing_prices.csv'
processed_data = []

with open(input_csv, mode='r', newline='', encoding='utf-8') as infile:
    reader = csv.reader(infile)
    next(reader) # Skip the header

    for row in reader:
        if row:
            non_empty_values = [value for value in row if value.strip()]
            if len(non_empty_values) > 1:
                address = non_empty_values[0]
                price = non_empty_values[1] # The second value is the average price
                processed_data.append({'Address': address, 'Price': price})
            elif len(non_empty_values) == 1:
                processed_data.append({'Address': non_empty_values[0], 'Price': '0'})

price_df = pd.DataFrame(processed_data)
price_df['Price'] = pd.to_numeric(price_df['Price'], errors='coerce').fillna(0).round(0).astype(int)


# --- 2. LOAD THE GEOJSON MAP DATA ---
local_geojson_file = 'limites-administratives-agglomeration-nad83.geojson'
gdf = gpd.read_file(local_geojson_file)


# --- 3. MERGE DATA AND CALCULATE PROJECTIONS (USING CPI) ---
name_mapping = {
    "Côte-des-Neiges–Notre-Dame-de-Grâce": "Côte-des-Neiges-Notre-Dame-de-Grâce",
    "Côte-des-Neiges-Notre-Dame-de-Grâce": "Côte-des-Neiges-Notre-Dame-de-Grâce",
    "L'Île-Bizard–Sainte-Geneviève": "L'Ile-Bizard",
    "L'Île-Bizard-Sainte-Geneviève": "L'Ile-Bizard",
    "L'Île-Dorval": "L'Ile-Dorval",
    "Mercier–Hochelaga-Maisonneuve": "Mercier-Hochelaga-Maisonneuve",
    "Mercier-Hochelaga-Maisonneuve": "Mercier-Hochelaga-Maisonneuve",
    "Le Plateau-Mont-Royal": "Plateau-Mont-Royal",
    "Le Sud-Ouest": "Sud-Ouest",
    "Rivière-des-Prairies–Pointe-aux-Trembles": "Rivière-des-Prairies–Pointe-aux-Trembles",
    "Rosemont–La Petite-Patrie": "Rosemont–La Petite-Patrie",
    "Villeray–Saint-Michel–Parc-Extension": "Villeray–Saint-Michel–Parc-Extension"
}

gdf['csv_name'] = gdf['NOM'].map(name_mapping).fillna(gdf['NOM'])
merged_gdf = gdf.merge(price_df, left_on='csv_name', right_on='Address', how='left')
merged_gdf['Price'] = merged_gdf['Price'].fillna(0).astype(int)

# CPI LOGIC
future_df = train_evaluate_and_predict()
current_yr_cpi = future_df.loc[0, "predicted_cpi"]
cpi_rates = [future_df.loc[i, "predicted_cpi"] for i in range(1, 6)]

merged_gdf.rename(columns={'Price': 'Price_0yr'}, inplace=True)

for i in range(5):
    year = i + 1
    future_cpi = cpi_rates[i]
    col_name = f'Price_{year}yr'

    if current_yr_cpi > 0:
        cpi_ratio = future_cpi / current_yr_cpi
    else:
        cpi_ratio = 1.0

    merged_gdf[col_name] = merged_gdf['Price_0yr'].apply(
        lambda price: (price * cpi_ratio) if price > 0 else 0
    ).round(0).astype(int)


# --- 4. CREATE THE MAP AND MULTIPLE LAYERS ---
columns_to_keep = [
    'geometry', 'csv_name', 'NOM',
    'Price_0yr', 'Price_1yr', 'Price_2yr', 'Price_3yr', 'Price_4yr', 'Price_5yr'
]
merged_gdf = merged_gdf[columns_to_keep]

m = folium.Map(location=[45.5017, -73.5673], zoom_start=10, tiles='CartoDB positron')

def get_color(price):
    if price > 2500: return '#f03b20'
    if price > 2000: return '#fd8d3c'
    if price > 1600: return '#feb24c'
    if price > 1200: return '#fed976'
    if price > 0:    return '#ffeda0'
    return '#ffffcc'

for year in range(6):
    price_col = f'Price_{year}yr'
    layer_name = 'Current (0 Yr)' if year == 0 else f'{year} Year Projection'

    folium.GeoJson(
        merged_gdf,
        name=layer_name,
        show=(year == 0),
        style_function=lambda feature, col=price_col: {
            'fillColor': get_color(feature['properties'][col]),
            'fillOpacity': 0.7,
            'weight': 0.3,
            'color': '#444'
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['NOM', price_col],
            # ** CHANGE 1: Added $ sign to the Price alias **
            aliases=['Municipality:', 'Projected Price: $'],
            localize=True,
            sticky=False,
            style="""
                background-color: #F0EFEFEF;
                border: 2px solid black;
                border-radius: 3px;
                box-shadow: 3px;
                color: #333;
                font-family: sans-serif;
                font-size: 14px;
            """
        ),
        highlight_function=lambda x: {'weight': 3, 'color': '#FFF', 'fillOpacity': 0.5}
    ).add_to(m)


# --- 5. ADD LAYER CONTROL (THE "BUTTONS") AND CUSTOM JS ---
folium.LayerControl().add_to(m)

# ** FIX: Custom JavaScript to enforce radio-button behavior (no stacking) **
# This script is now added to the map's root, which is a better injection point.
script = """
<script type="text/javascript">
    function setupProjectionControl() {
        var overlays = document.querySelector('.leaflet-control-layers-overlays');
        if (overlays) {
            // Add a title for clarity
            var title = document.createElement('div');
            title.innerHTML = '<strong>Price Projections:</strong>';
            title.style.padding = '5px 0 0 5px';
            title.style.fontWeight = 'bold';
            overlays.prepend(title);

            // Find all checkboxes within the overlays section
            var checkboxes = overlays.querySelectorAll('input[type="checkbox"]');

            // Apply a name attribute to make them mutually exclusive (radio buttons)
            checkboxes.forEach(function(checkbox) {
                // Apply the same name attribute to make them behave like radio buttons
                checkbox.setAttribute('name', 'projection-layer-group');

                // OPTIONAL: Add some styling for better UI
                checkbox.style.marginRight = '8px';
                checkbox.parentNode.style.marginBottom = '5px';
                checkbox.parentNode.style.cursor = 'pointer';

                // Attach click handler to ensure only one is selected
                checkbox.addEventListener('click', function() {
                    if (this.checked) {
                        checkboxes.forEach(function(cb) {
                            if (cb !== checkbox) {
                                cb.checked = false;
                                // Manually trigger the Leaflet event to hide the map layer
                                cb.dispatchEvent(new Event('change'));
                            }
                        });
                    }
                    // Manually trigger the Leaflet event for the currently clicked checkbox
                    // to ensure the corresponding map layer is shown/hidden
                    this.dispatchEvent(new Event('change'));
                });
            });

            // Set the first layer as checked and trigger its change event to show it
            if (checkboxes.length > 0) {
                checkboxes.forEach(cb => cb.checked = false); // Uncheck all first
                checkboxes[0].checked = true; // Check the default layer (Current Prices)
                checkboxes[0].dispatchEvent(new Event('change')); // Show the default layer
            }
        }
    }
    // Wait for the document structure to be ready before running setup
    document.addEventListener('DOMContentLoaded', setupProjectionControl);
</script>
"""
# Add the script to the map's HTML head
m.get_root().html.add_child(Element(script))


# --- 6. SAVE THE MAP ---
output_map_filename = 'montreal_map_with_prices.html'
m.save(output_map_filename)

print(f"Success! Map with projections saved to {output_map_filename}")
