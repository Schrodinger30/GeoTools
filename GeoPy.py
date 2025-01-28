# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 09:21:00 2024

@author: C53585
"""

import folium
import cbsodata
import pandas as pd
import folium.plugins
import geopandas as gpd
from folium.map import Marker, Template, FeatureGroup
 

class GeoPy():
    
    def __init__(self):
        """ Initialise the class 'GeoPy'
        
        Args:
            None
        
        Returns:
            None
        """
        
        self.__version__ = "0.1.0"
        
        return None
    
    
    def get_pdok_data(self, url, crs):
        """ Get geodatasets from PDOK (https://www.pdok.nl/).
            PDOK provides over 200 dutch governmental geodatasets.
            Datasets are delivered using WMS or WFS.
        
        Args:
            url (str):  PDOK dataset accessPoint URL
            
            crs (str):  Coordinate Reference System to be used
            
                        EPSG:28992 for Netherlands - onshore, 
                        including Waddenzee, Dutch Wadden Islands 
                        and 12-mile offshore coastal zone
        
        Returns:
            geo_layer (datatype):   Geographical layer based on PDOK data
        """
        
        # Read data 
        geo_layer = gpd.read_file(url)
        
        # Set Coordinate Reference System (CRS)
        geo_layer.crs = crs
        geo_layer = geo_layer.to_crs({"proj" : "merc"})
        
        # Add geo ID to each row for visualization purposes
        geo_layer['geoid'] = geo_layer.index.astype(str)
        
        return geo_layer
    
    
    def get_cbs_data(self, cbs_id):
        """ Get data from the open data interface of Statistics NL (CBS)
            using CBS open data portal (package: cbsodata)
        
        Args:
            cbs_id (str):  Unique Identifier of the table
        
        Returns:
            cbs_data (dataframe): Dataframe containing selected CBS dataset
        """
        
        # Get CBS dataset
        cbs_data = pd.DataFrame(cbsodata.get_data(cbs_id))
        
        return cbs_data
    
    
    def prepare_pc6_data(self):
        """ Prepare CBS statistical data on postalcode level
        
            https://shorturl.at/XLyfA
        
        Args:
            cbs_id (str):  Unique Identifier of the table
        
        Returns:
            cbs_data (dataframe): Dataframe containing selected CBS dataset
        """
        
    
    
    def prepare_folium_map(self, 
                           centerpoint_lat=None,
                           centerpoint_lon=None,
                           tile_name=None):
        """ Prepare folium basemap
        
        Args:
            centerpoint_lat (float):    Centerpoint latitude
                                        Defaults to 41.000150980792405
            centerpoint_lon (float):    Centerpoint longitude
                                        Defaults to 34.99998540139929
            tile (str):                 Tile used on map
                                        Defaults to 'cartodbpositron'
        
        Returns:
            folium_map (datatype): Folium basemap
        """
        
        # Set centerpoint coordinates
        if centerpoint_lat == None:
            centerpoint_coords = (41.000150980792405, 34.99998540139929)
        else:
            centerpoint_coords = (centerpoint_lat, centerpoint_lon)
            
        # Set basemap tile
        if tile_name == None:
            tile_name = "cartodbpositron"
        else:
            tile_name = tile_name
            
        # Create basemap with selected tile and centerpoint coordinates   
        folium_map = folium.Map(location = centerpoint_coords,
                                tiles = tile_name,
                                zoom_start=7,
                                control_scale = True,
                                control = False)
        
        # Add fullscreen functionality to map
        folium.plugins.Fullscreen().add_to(folium_map)
        
        # Add layer control
        #folium.LayerControl().add_to(folium_map)
        
        return folium_map
    
    
    def choropleth_layer(self,
                         geo_data,
                         data,
                         columns,
                         fill_color,
                         nan_fill_color,
                         legend_name,
                         name,
                         highlight = True,
                         control = True,
                         overlay = False,
                         show = True
                         ):
        """ Create choropleth layer to add to folium basemap
        
        Args:
            centerpoint_lat (float):    Centerpoint latitude
                                        Defaults to 41.000150980792405
            centerpoint_lon (float):    Centerpoint longitude
                                        Defaults to 34.99998540139929
            tile (str):                 Tile used on map
                                        Defaults to 'cartodbpositron'
        
        Returns:
            choropleth_layer (datatype): Choropleth layer 
        """
        
        choro_layer = folium.Choropleth(geo_data = geo_data,
                                        data = data,
                                        columns = columns,
                                        key_on = "feature.id",
                                        fill_color = fill_color,
                                        nan_fill_color = nan_fill_color,
                                        legend_name = legend_name,
                                        name = name,
                                        highlight = highlight,
                                        control = control,
                                        overlay = overlay,
                                        show = True
                                        )
        
        return choro_layer
        
    
        