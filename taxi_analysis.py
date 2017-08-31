# Analyze the taxi drop-off data to determine airline market share
from collections import Counter
from ast import literal_eval as make_tuple

import pandas as pd
import numpy as np

def main():
    # Load drop-off data from modified csv's
    jfk_green_dropoffs = pd.DataFrame.from_csv(
        './2016/modified/mod-tlc-green-jfk-dropoffs-2016.csv'
    )
    jfk_yellow_dropoffs = pd.DataFrame.from_csv(
        './2016/modified/mod-tlc-yellow-jfk-dropoffs-2016.csv'
    )
    newark_green_dropoffs = pd.DataFrame.from_csv(
        './2016/modified/mod-tlc-green-newark-dropoffs-2016.csv'
    )
    newark_yellow_dropoffs = pd.DataFrame.from_csv(
        './2016/modified/mod-tlc-yellow-newark-dropoffs-2016.csv'
    )
    laguardia_green_dropoffs = pd.DataFrame.from_csv(
        './2016/modified/mod-tlc-green-laguardia-dropoffs-2016.csv'
    )
    laguardia_yellow_dropoffs = pd.DataFrame.from_csv(
        './2016/modified/mod-tlc-yellow-laguardia-dropoffs-2016.csv'
    )

    # Count the number of passengers dropped off at each terminal
    newark_yellow_terminal_counts = count_passengers(newark_yellow_dropoffs)
    newark_green_terminal_counts = count_passengers(newark_green_dropoffs)
    total_newark_counts = newark_green_terminal_counts + newark_yellow_terminal_counts

    laguardia_yellow_terminal_counts = count_passengers(laguardia_yellow_dropoffs)
    laguardia_green_terminal_counts = count_passengers(laguardia_green_dropoffs)
    total_laguardia_counts = laguardia_green_terminal_counts + laguardia_yellow_terminal_counts

    jfk_yellow_terminal_counts = count_passengers(jfk_yellow_dropoffs)
    jfk_green_terminal_counts = count_passengers(jfk_green_dropoffs)
    total_jfk_counts = jfk_green_terminal_counts + jfk_yellow_terminal_counts

    # Evenly distribute the terminal passengers among airlines,
    # aggregating across all airports and terminals
    dropoff_counts = add_counts(total_newark_counts['terminal_a'], Counter(),
        make_airline_array(
            """Southwest
            Air Canada
            Virgin America
            JetBlue Airways
            American
            Alaska"""
        )
    )
    dropoff_counts = add_counts(total_newark_counts['terminal_b'], dropoff_counts,
        make_airline_array(
            """Austrian
            Cathay Pacific Airways
            TAP Air Portugal
            Allegiant Air
            OpenSkies
            Aer Lingus
            Porter Airlines
            Delta
            SAS Scandinavian
            Spirit
            Swiss International
            Virgin Atlantic Airways
            Ethiopian
            Wow Air
            Lufthansa
            Air India
            El Al
            Icelandair
            Air China
            British Airways"""
        )
    )
    dropoff_counts = add_counts(total_newark_counts['terminal_c'], dropoff_counts,
        make_airline_array(
            """United"""
        )
    )
    dropoff_counts = add_counts(total_laguardia_counts['terminal_a'], dropoff_counts,
        make_airline_array(
            """Delta"""
        )
    )
    dropoff_counts = add_counts(total_laguardia_counts['terminal_b'] , dropoff_counts,
        make_airline_array(
            """American
            JetBlue
            Spirit
            Southwest
            Air Canada
            Virgin America
            Frontier
            United"""
        )
    )
    dropoff_counts = add_counts(total_laguardia_counts['terminal_c'], dropoff_counts,
        make_airline_array(
            """Delta
            American"""
        )
    )

    dropoff_counts = add_counts(total_laguardia_counts['terminal_d'], dropoff_counts,
        make_airline_array(
            """Delta
            WestJet""")
        )

    dropoff_counts = add_counts(total_jfk_counts['terminal_1'], dropoff_counts,
        make_airline_array(
            """Cayman Airways
            Air France
            Norwegian Air Shuttle
            Azerbaijan Hava Yollary
            Fly Jamaica
            Saudia
            Austrian
            Aeromexico
            Turkish
            EVA Air
            Interjet
            Alitalia
            Japan
            Aeroflot Russian
            Korean Air Lines
            Brussels
            China Eastern
            Lufthansa
            Air China
            Meridiana
            Philippine
            Royal Air Maroc"""
        )
    )
    dropoff_counts = add_counts(total_jfk_counts['terminal_2'], dropoff_counts,
        make_airline_array(
            """Delta"""
        )
    )
    dropoff_counts = add_counts(total_jfk_counts['terminal_4'], dropoff_counts,
        make_airline_array(
            """Air Serbia
            Arik Air
            El Al
            Volaris
            Egyptair
            Air Jamaica
            XL Airways
            China
            Thomas Cook
            Uzbekistan
            Air Europa
            Virgin America
            Singapore
            Etihad
            China Southern
            Avianca
            Virgin Atlantic Airways
            Pakistan
            COPA
            Kuwait Airways
            Carribean
            Emirates
            KLM
            Asiana
            Sun Country
            Swiss International
            WestJet
            Air India
            Miami Air
            Delta
            South African Airways"""
        )
    )
    dropoff_counts = add_counts(total_jfk_counts['terminal_5'], dropoff_counts,
        make_airline_array(
            """JetBlue
            Hawaiian
            Aer Lingus
            TAP Air Portugal"""
        )
    )
    dropoff_counts = add_counts(total_jfk_counts['terminal_7'], dropoff_counts,
        make_airline_array(
            """Qatar Airways
            Ukraine International
            Cathay Pacific Airways
            Iberia
            Icelandair
            OpenSkies
            LOT Polish
            Qantas
            Interjet
            British Airways
            ANA
            Aerolineas Argentinas"""
        )
    )
    dropoff_counts = add_counts(total_jfk_counts['terminal_8'], dropoff_counts,
        make_airline_array(
            """American Eagle
            American
            Alaska
            Air Berlin
            Qatar Airways
            Royal Jordanian
            Finnair"""
        )
    )

    # Calculate total number of drop-offs
    total_dropoffs = sum(dropoff_counts.values())

    # Print airline passengers in top-down fashion
    print dropoff_counts.most_common()

    # Initialize market share counter
    market_share = Counter()

    # Calculate percent market share for each airline
    for airline, dropoffs in dropoff_counts.most_common():
        market_share[airline] = dropoffs/float(total_dropoffs) * 100

    # Print airline market shares in top-down fashion
    print market_share.most_common()

# Function to count the number of passengers who flew out of each terminal
def count_passengers(df):
    # Initialize terminal count Series
    terminal_counts = pd.Series(
        np.zeros(len(df['terminal'].unique())),
        index=df['terminal'].unique(),
        name='terminal'
    )
    # Iterate over the drop-offs to add passenger counts
    # If there is no passenger data, default to one passenger
    for _, dropoff in df.iterrows():
        if not np.isnan(dropoff['passenger_count']):
            terminal_counts[dropoff['terminal']] += dropoff['passenger_count']
        else:
            terminal_counts[dropoff['terminal']] += 1
    return terminal_counts

# Function to evenly distribute terminal drop-offs among airlines servicine
# that terminal
def add_counts(total_dropoff_count, dropoff_counts, terminal_airline_list):
    average_dropoff_count = total_dropoff_count/len(terminal_airline_list)
    for airline in terminal_airline_list:
        dropoff_counts[airline] += average_dropoff_count
    return dropoff_counts

# Function to make an airline array from a raw string
def make_airline_array(raw_string):
    return raw_string.split('\n')

if __name__ == '__main__':
    main()
