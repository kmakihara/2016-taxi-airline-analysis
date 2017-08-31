# Transforms data into a more analysis friendly format
import pandas as pd
import numpy as np
import shapefile

from ast import literal_eval as make_tuple
from shapely.geometry import shape, Point
from pyproj import Proj, transform
from geopy.distance import great_circle
from constants import (
    NEWARK_ID,
    LAGUARDIA_ID,
    JFK_ID,
    NEWARK_COORDINATES,
    LAGUARDIA_COORDINATES,
    JFK_COORDINATES
)

def main():
    # Import shapefile containing TLC taxi zones
    sf = shapefile.Reader("taxi_zones/taxi_zones")
    shapes = sf.shapes()

    # Load taxi drop-offs from csv files downloaded from google storage
    newark_yellow_dropoffs = pd.DataFrame.from_csv(
        './2016/tlc-yellow-newark-dropoffs-2016.csv'
    )
    newark_green_dropoffs = pd.DataFrame.from_csv(
        './2016/tlc-green-newark-dropoffs-2016.csv'
    )
    laguardia_yellow_dropoffs = pd.DataFrame.from_csv(
        './2016/tlc-yellow-laguardia-dropoffs-2016.csv'
    )
    laguardia_green_dropoffs = pd.DataFrame.from_csv(
        './2016/tlc-green-laguardia-dropoffs-2016.csv'
    )
    jfk_yellow_dropoffs = pd.DataFrame.from_csv(
        './2016/tlc-yellow-jfk-dropoffs-2016.csv'
    )
    jfk_green_dropoffs = pd.DataFrame.from_csv(
        './2016/tlc-green-jfk-dropoffs-2016.csv'
    )

    # Add coordinates column to drop-off dataframes
    newark_yellow_dropoffs['coords'] = add_coords(newark_yellow_dropoffs)
    newark_green_dropoffs['coords'] = add_coords(newark_green_dropoffs)
    laguardia_yellow_dropoffs['coords'] = add_coords(laguardia_yellow_dropoffs)
    laguardia_green_dropoffs['coords'] = add_coords(laguardia_green_dropoffs)
    jfk_yellow_dropoffs['coords'] = add_coords(jfk_yellow_dropoffs)
    jfk_green_dropoffs['coords'] = add_coords(jfk_green_dropoffs)

    # Create screens to filter out drop-offs downloaded from google storage
    # not actually within the TLC airport drop-off zone. This code takes a while to run...
    newark_yellow_filter = newark_yellow_dropoffs['coords'].apply(
        check_bounds, args=(shapes[NEWARK_ID - 1],))
    newark_green_filter = newark_green_dropoffs['coords'].apply(
        check_bounds, args=(shapes[NEWARK_ID - 1],))
    laguardia_green_filter = laguardia_green_dropoffs['coords'].apply(
        check_bounds, args=(shapes[LAGUARDIA_ID - 1],))
    laguardia_yellow_filter = laguardia_yellow_dropoffs['coords'].apply(
        check_bounds, args=(shapes[LAGUARDIA_ID - 1],))
    jfk_yellow_filter = jfk_yellow_dropoffs['coords'].apply(
        check_bounds, args=(shapes[JFK_ID - 1],))
    jfk_green_filter = jfk_green_dropoffs['coords'].apply(
        check_bounds, args=(shapes[JFK_ID - 1],))

    # Apply screens to drop-off dataframes
    newark_yellow_dropoffs = newark_yellow_dropoffs.loc[newark_yellow_filter]
    newark_green_dropoffs = newark_green_dropoffs.loc[newark_green_filter]
    laguardia_yellow_dropoffs = laguardia_yellow_dropoffs.loc[laguardia_yellow_filter]
    laguardia_green_dropoffs = laguardia_green_dropoffs.loc[laguardia_green_filter]
    jfk_yellow_dropoffs = jfk_yellow_dropoffs.loc[jfk_yellow_filter]
    jfk_green_dropoffs = jfk_green_dropoffs.loc[jfk_green_filter]

    # Assign terminal to each drop-off and add terminal column to drop-off dataframe
    # I chose to use np.vectorize rather than series.apply since np.vectorize had
    # noticeably better performance in this situation. With the screens, the
    # performance improvement was negligible so I decided to use apply
    newark_yellow_dropoffs['terminal'] = np.vectorize(find_terminal)(
        newark_yellow_dropoffs['coords'], NEWARK_COORDINATES
    )
    newark_green_dropoffs['terminal'] = np.vectorize(find_terminal)(
        newark_green_dropoffs['coords'], NEWARK_COORDINATES
    )
    laguardia_yellow_dropoffs['terminal'] = np.vectorize(find_terminal)(
        laguardia_yellow_dropoffs['coords'], LAGUARDIA_COORDINATES
    )
    laguardia_green_dropoffs['terminal'] = np.vectorize(find_terminal)(
        laguardia_green_dropoffs['coords'], LAGUARDIA_COORDINATES
    )
    jfk_yellow_dropoffs['terminal'] = np.vectorize(find_terminal)(
        jfk_yellow_dropoffs['coords'], JFK_COORDINATES
    )
    jfk_green_dropoffs['terminal'] = np.vectorize(find_terminal)(
        jfk_green_dropoffs['coords'], JFK_COORDINATES
    )

    # Export modified drop-off dataframes to csv for later use.
    jfk_green_dropoffs.to_csv('./2016/modified/mod-tlc-green-jfk-dropoffs-2016.csv')
    jfk_yellow_dropoffs.to_csv('./2016/modified/mod-tlc-yellow-jfk-dropoffs-2016.csv')
    newark_green_dropoffs.to_csv('./2016/modified/mod-tlc-green-newark-dropoffs-2016.csv')
    newark_yellow_dropoffs.to_csv('./2016/modified/mod-tlc-yellow-newark-dropoffs-2016.csv')
    laguardia_green_dropoffs.to_csv('./2016/modified/mod-tlc-green-laguardia-dropoffs-2016.csv')
    laguardia_yellow_dropoffs.to_csv('./2016/modified/mod-tlc-yellow-laguardia-dropoffs-2016.csv')

# Assigns drop-off a terminal based on nearest great-circle distance
# Great-circle distance is the distance between two points on a sphere
def find_terminal(drop_off_coords, terminal_coords):
    min_distance = float('inf')
    min_terminal = ''

    # Calculates minimum great-circle distance
    for terminal, coords in terminal_coords.iteritems():
        distance = great_circle(drop_off_coords, coords).meters
        if distance < min_distance:
            min_distance = distance
            min_terminal = terminal

    return min_terminal

# Helper function to add coordinate column to drop-off dataframe
def add_coords(df):
    return list(zip(df['dropoff_latitude'], df['dropoff_longitude']))

# Function to check whether the drop-off is within the given TLC zones
# This is used to filter out trips that were downloaded from bigquery
# because they fell within the bounding box but don't actually fall within
# the TLC airport drop-off zone
def check_bounds(raw_coords, shapefile):
    # Transforms the location units from epsg:2263 to latitude longitude coordinates (epsg:4326)
    in_proj = Proj(init='epsg:4326')
    out_proj= Proj(init='epsg:2263', preserve_units = True)
    coords = raw_coords
    if isinstance(raw_coords, str):
        coords = make_tuple(raw_coords)


    point = Point(transform(in_proj, out_proj, coords[1], coords[0]))
    polygon = shape(shapefile)

    # Checks whether TLC zone contains drop-off point
    return polygon.contains(point)

if __name__ == '__main__':
    main()
