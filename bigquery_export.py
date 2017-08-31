# Helper script to export bigquery data
import uuid
import shapefile

from google.cloud import bigquery
from pyproj import Proj, transform
from constants import NEWARK_ID, LAGUARDIA_ID, JFK_ID, PROJECT_ID

def main():

    # Instantiates a client
    bigquery_client = bigquery.Client(project=PROJECT_ID)

    # Import shapefile containing TLC taxi zones
    sf = shapefile.Reader("taxi_zones/taxi_zones")
    shapes = sf.shapes()

    # Get the bounding boxes of each airport
    newark_bounds = get_bounds(shapes[NEWARK_ID - 1])
    laguardia_bounds = get_bounds(shapes[LAGUARDIA_ID - 1])
    jfk_bounds = get_bounds(shapes[JFK_ID - 1])

    # Export TLC bigquery data and saving it to csv files.
    # These csv files are then manually downloaded from google storage
    export_data(
        bigquery_client,
        laguardia_bounds,
        'tlc_yellow_trips_2016',
        'gs://farallon-taxi-analysis/tlc-yellow-laguardia-dropoffs-2016.csv'
    )
    export_data(
        bigquery_client,
        laguardia_bounds,
        'tlc_green_trips_2016',
        'gs://farallon-taxi-analysis/tlc-green-laguardia-dropoffs-2016.csv'
    )
    export_data(
        bigquery_client,
        newark_bounds,
        'tlc_yellow_trips_2016',
        'gs://farallon-taxi-analysis/tlc-yellow-newark-dropoffs-2016.csv'
    )
    export_data(
        bigquery_client,
        newark_bounds,
        'tlc_green_trips_2016',
        'gs://farallon-taxi-analysis/tlc-green-newark-dropoffs-2016.csv'
    )
    export_data(
        bigquery_client,
        jfk_bounds,
        'tlc_yellow_trips_2016',
        'gs://farallon-taxi-analysis/tlc-yellow-jfk-dropoffs-2016.csv'
    )
    export_data(
        bigquery_client,
        jfk_bounds,
        'tlc_green_trips_2016',
        'gs://farallon-taxi-analysis/tlc-green-jfk-dropoffs-2016.csv'
    )

# Returns a bounding box around the given shapefile (TLC airport zone)
def get_bounds(shape):
    # transforms the location units from epsg:2263 to latitude longitude coordinates (epsg:4326)
    in_proj = Proj(init='epsg:2263', preserve_units = True)
    out_proj = Proj(init='epsg:4326')
    x1, y1 = shape.bbox[0], shape.bbox[1]
    x2, y2 = shape.bbox[2], shape.bbox[3]
    new_x1, new_y1 = transform(in_proj, out_proj, x1, y1)
    new_x2, new_y2 = transform(in_proj, out_proj, x2, y2)

    return [new_x1, new_y1, new_x2, new_y2]

# Downloads and exports the TLC bigquery data to json files
def export_data(client, query_bounds, dataset, destinationUri):
    # SQL query string returning trip data with drop-off coordinates within the given bounding box
    query_string = """
        SELECT
            *
        FROM [bigquery-public-data:new_york.{}]
        WHERE
            /* Return values between a pair of */
            /* latitude and longitude coordinates */
            dropoff_latitude > {} AND
            dropoff_latitude < {} AND
            dropoff_longitude > {} AND
            dropoff_longitude < {}
    """.format(dataset, query_bounds[1], query_bounds[3], query_bounds[0], query_bounds[2])

    # Initialize the query
    query_job = client.run_async_query(str(uuid.uuid4()), query_string)
    query_job.begin()
    query_job.result()

    destination_table = query_job.destination
    destination_table.reload()

    # Export data to Google Storage (data can only be downloaded to local disks from google storage)
    export_job_name = str(uuid.uuid4())
    export_job = client.extract_table_to_storage(export_job_name, destination_table, destinationUri)

    export_job.begin()
    export_job.result()  # Wait for job to complete

    print 'Exported {} to {}'.format(destination_table, destinationUri)

if __name__ == '__main__':
    main()
