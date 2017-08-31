# 2016-taxi-airline-analysis
Analysis of NYC airline market share based off of taxi drop offs at Newark, LaGuardia, and JFK airport terminals

Run ``` python bigquery_export.py``` to export data from Google BigQuery to Google Storage

Download files from Google Storage to local disk and store in the project directory

Run ``` python transform_data.py ``` to transform local data to include drop-off coordinates, terminals, etc...

Run ``` python taxi_analysis.py``` to analyze drop-off data and estimate airline market share.
