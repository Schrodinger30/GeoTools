# Import packages
import GeoTools
import pandas as pd

# Instantiate GeoTools class
gt = GeoTools.GeoTools()


# Example 1: Get location data using Nominatim API
# ----------------------------------------------------------------------------
# Example locations in the Netherlands
data = {'Name': ['Anne Frank House','Van Gogh Museum','Rijksmuseum',
                 'Keukenhof','Efteling','Markthal','Giethoorn',''],
        'Street': ['','','','','','','','John Adams Park'],
        'Number': ['','','','','','','','1'],
        'PostalCode': ['','','','','','','','2244BZ'],
        'City': ['Amsterdam','Amsterdam','Amsterdam','','','Rotterdam',
                 '','Wassenaar'],
        'Country': ['NL','NL','NL','NL','NL','NL','NL','NL']}

# Create dataframe from locations
locations = pd.DataFrame(data)

# Get OSM data for each location
location_data = gt.geocoder_nominatim(locations,
                                      'Name',
                                      'Street',
                                      'Number',
                                      'PostalCode',
                                      'City',
                                      'Country')

# Example 2: Add location markers
# ----------------------------------------------------------------------------
# Create map
m = gt.prepare_folium_map(tile_name="openstreetmap")

markers_map = gt.location_markers(location_data,
                                  "lat",
                                  "lon",
                                  add_to_existing_map=True,
                                  map_to_use=m)
                                  
markers_map.save('.\output\markers_map.html')
