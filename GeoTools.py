import time
import folium
import cbsodata
import pandas as pd
import folium.plugins
from tqdm import tqdm
import geopandas as gpd
from geopy.geocoders import Nominatim
from folium.map import Marker, Template, FeatureGroup


class GeoTools:

    def __init__(self):
        """Initialise the class 'GeoTools'

        Args:
            None

        Returns:
            None
        """

        self.__version__ = "0.1.0"

        return None

    def get_pdok_data(self, url, crs):
        """Get geodatasets from PDOK (https://www.pdok.nl/).
            PDOK provides over 200 dutch governmental geodatasets.
            Datasets are delivered using WMS or WFS.

        Args:
            url (str):              PDOK dataset accessPoint URL

            crs (str):              Coordinate Reference System to be used

                                    EPSG:28992 for Netherlands - onshore,
                                    including Waddenzee, Dutch Wadden Islands
                                    and 12-mile offshore coastal zone

        Returns:
            geo_layer (object):     Geographical layer based on PDOK data
        """

        # Read data
        geo_layer = gpd.read_file(url)

        # Set Coordinate Reference System (CRS)
        geo_layer.crs = crs
        geo_layer = geo_layer.to_crs({"proj": "merc"})

        # Add geo ID to each row for visualization purposes
        geo_layer["geoid"] = geo_layer.index.astype(str)

        return geo_layer

    def get_cbs_data(self, cbs_id):
        """Get data from the open data interface of Statistics NL (CBS)
            using CBS open data portal (package: cbsodata)

        Args:
            cbs_id (str):           Unique Identifier of the table

        Returns:
            cbs_data (dataframe):   Dataframe containing selected CBS dataset
        """

        # Get CBS dataset
        cbs_data = pd.DataFrame(cbsodata.get_data(cbs_id))

        return cbs_data

    def geocoder_nominatim(
        self,
        df,
        ObjectName,
        ObjectStreet,
        ObjectNumber,
        ObjectPostalCode,
        ObjectCity,
        ObjectCountry,
    ):
        """Geocoding using Nominatim API (https://wiki.openstreetmap.org/wiki/Nominatim)

        Args:
            df (dataframe):             Dataframe containing the objects

            ObjectName (str):           Columnname containing object name

            ObjectStreet (str):         Columnname containing object streetname

            ObjectNumber (str):         Columnname containing object number

            ObjectPostalCode (str):     Columnname containing object postalcode

            ObjectCity (str):           Columnname containing object city

            ObjectCountry (str):        Columnname containing object country

        Returns:
            locs_list (dataframe):      Dataframe of collected OSM data for each object
        """

        # Create emtpy list to store location data for each row
        locs_list = []

        # Iterate through dataframe and collect location data for each object
        for index, row in tqdm(
            df.iterrows(), total=df.shape[0], desc="Get location data from OSM"
        ):

            # Define query
            query = (
                row[ObjectName]
                + ","
                + row[ObjectStreet]
                + " "
                + row[ObjectNumber]
                + ","
                + row[ObjectPostalCode]
                + ","
                + row[ObjectCity]
                + ","
                + row[ObjectCountry]
            )

            # Initiate API
            app = Nominatim(user_agent="GeoTools")

            try:
                # Get data from API
                loc = app.geocode(query).raw

                # Initiate 1 second wait before next request due to API limits
                time.sleep(1)

                # Append collected location data to list
                locs_list.append(loc)

            except:
                # If no data can be collected append empty dictionary to list
                locs_list.append({})

        return pd.DataFrame(locs_list)

    def prepare_folium_map(
        self,
        centerpoint_lat=None,
        centerpoint_lon=None,
        tile_name="openstreetmap",
        layercontrol=True,
        fullscreen=True,
        minimap=False,
        oms=False,
    ):
        """Prepare folium basemap

        Args:
            centerpoint_lat (float):    Centerpoint latitude
                                        Defaults to 41.000150980792405

            centerpoint_lon (float):    Centerpoint longitude
                                        Defaults to 34.99998540139929

            tile (str):                 Tile used on map
                                        Defaults to 'cartodbpositron'

            fullscreen (boolean):       Boolean to enable / disable fullscreen toggle button

            minimap (boolean):          Boolean to enable / disable minimap

            oms (boolean):              Boolean to enable / disable functionality to 'spiderfy'
                                        overlapping markers when clicked.

        Returns:
            folium_map (object):        Folium basemap
        """

        # Set centerpoint coordinates
        if centerpoint_lat == None:
            centerpoint_coords = (41.000150980792405, 34.99998540139929)
        else:
            centerpoint_coords = (centerpoint_lat, centerpoint_lon)

        # Create basemap with selected tile and centerpoint coordinates
        folium_map = folium.Map(
            location=centerpoint_coords,
            tiles=tile_name,
            zoom_start=7,
            control_scale=True,
            control=False,
        )

        # Add fullscreen functionality to map
        if fullscreen:
            folium.plugins.Fullscreen().add_to(folium_map)

        # Add layer control
        folium.LayerControl().add_to(folium_map)

        return folium_map

    def location_markers(
        self,
        locations,
        latitude,
        longitude,
        name=None,
        icon="map-pin",
        color="orange",
        tooltip=False,
        tooltip_text=None,
        popup=False,
        antpath=None,
        add_to_existing_map=False,
        map_to_use=None
    ):
        """Create markers from coordinates

        Args:
            locations (dataframe):          Dataframe containing all locations

            latitude (float):               Latitude of marker

            longitude (float):              Longitude of marker

            icon (boolean):                 Boolean to enable / disable fullscreen toggle button
            
            color (str):                    Marker color. Available colors: 'red','blue','green',
                                                'purple','orange','darkred','lightred','beige',
                                                'darkblue','darkgreen','cadetblue','darkpurple',
                                                'white','pink','lightblue','lightgreen','gray',
                                                'black','lightgray'
                                                
            tooltip (boolean):              Boolean to enable / disable tooltip when hovering over marker
                
            tooltip_text (str):             String containing the tooltip text
                
            popup (boolean):                Boolean to enable / disable popup when clicking a marker
                                            Popup will be populated with the tooltip text

            add_to_existing_map (boolean):  Boolean to enable / disable usage of an existing folium map object

            map_to_use (object):            Name of an existing folium map object

        Returns:
            m (object):                     Folium basemap
        """
        
        if add_to_existing_map:
            m = map_to_use
        else:
            # Get average latitude and longitude from dataframe
            centerpoint_lat = pd.to_numeric(locations[latitude]).mean()
            centerpoint_lon = pd.to_numeric(locations[longitude]).mean()
            
            # Create map using mean latitude and longitude from dataframe
            # as centerpoint coordinates
            m = self.prepare_folium_map(centerpoint_lat=centerpoint_lat,
                                        centerpoint_lon=centerpoint_lon)
        
        # Create and add marker for each location in dataframe
        for index, row in locations.iterrows():
            folium.Marker(location=[row[latitude],row[longitude]],
                          icon=folium.Icon(color=color,
                                           icon=icon,
                                           prefix="fa"),
                          pathCoords=antpath
                          ).add_to(m)

        return m

    def markercluster(self):

        return None

    def polygon(self):

        return None

    def multipolygon(self):

        return None

    def linestring(self):

        return None

    def timestampedgeojson(self):

        return None

    def heatmap(self):

        return None

    def heatmapwithtime(self):

        return None

    def grouped_layercontrol(self):

        return None

    def choropleth_layer(
        self,
        geo_data,
        data,
        columns,
        fill_color,
        nan_fill_color,
        legend_name,
        name,
        highlight=True,
        control=True,
        overlay=False,
        show=True,
    ):
        """Create choropleth layer to add to folium basemap

        Args:
            centerpoint_lat (float):    Centerpoint latitude
                                        Defaults to 41.000150980792405

            centerpoint_lon (float):    Centerpoint longitude
                                        Defaults to 34.99998540139929

            tile (str):                 Tile used on map
                                        Defaults to 'cartodbpositron'

        Returns:
            choropleth_layer (object):  Choropleth layer
        """

        choro_layer = folium.Choropleth(
            geo_data=geo_data,
            data=data,
            columns=columns,
            key_on="feature.id",
            fill_color=fill_color,
            nan_fill_color=nan_fill_color,
            legend_name=legend_name,
            name=name,
            highlight=highlight,
            control=control,
            overlay=overlay,
            show=True,
        )

        return choro_layer
