import requests as rq
import datetime as dt
# import os
# import calendar
from pandas.tseries.offsets import BDay
import pandas as pd
import json

def get_cme_data():
    """
    This function takes no parameters and returns a tuple containing the trade_date_formatted [0], futures_data_df [1], and response.status_code [2]
    """
    # Request URL
    url = r"https://www.cmegroup.com/CmeWS/mvc/Quotes/Future/305/G"

    # Store response
    response = rq.get(url)

    if response.status_code > 299:
        return trade_date_formatted, futures_data_df, response.status_code
    else:
        # Format and print response
        response_json = response.json()
        futures_data_df = pd.json_normalize(response_json, record_path=['quotes'])


        ### GET TRADE DATE ###
        trade_date_df = pd.json_normalize(response_json)
        trade_date = trade_date_df['tradeDate'][0]

        trade_date_formatted = dt.datetime.strptime(trade_date, "%d %b %Y").date()
    
    return trade_date_formatted, futures_data_df, response.status_code



def get_futures_data():

    """
    This function takes no parameters, but will return a tuple containing the last trade_date[0] and futures_data [1] dataframe
    """

    # Get today's date. We'll use this to see if we need to retrieve new data.
    current_date = dt.datetime.today().date()
    current_date_weekday = current_date.weekday()

    # File names for saved data access
    # file_name = "date_file.txt"
    file_name = "files/date_file.txt"

    # Futures data file
    futures_data_csv_file = r"files/fed_funds_futures_quotes.csv"

    # Convert to last weekday if a weekend
    if current_date_weekday < 5: # Before Saturday
        current_biz_date = current_date
    elif current_date_weekday >= 5: # Sat or Sun
        current_biz_date = current_date - dt.timedelta(1)

    # Get the date the last time our csv file was uploaded
    date_file = open(file_name, "r")
    trade_date = date_file.read()
    date_file.close()
    # last_upload_date = '2023-06-12'
    last_upload_date = dt.datetime.strptime(trade_date, '%Y-%m-%d').date()

    # Check to see if we need to update the fed funds trade data
    if last_upload_date == current_biz_date:
        pass
    
    elif last_upload_date < current_biz_date:
        # Grab futures data from CME

        # If the status code is in the 200's, then we should have gotten good data back and can overwrite the file
        if get_cme_data()[2] <= 299:

            retrieve_dataframe = get_cme_data()[1]
           # Write it to csv
            retrieve_dataframe.to_csv(futures_data_csv_file, mode="w+")

            # Write new trade date to 
            trade_date = get_cme_data()[0]
            date_file = open(file_name, "w+")
            date_file.write(str(trade_date))
            date_file.close()

        # If the codes are not in the 200's, then we want to skip the overwriting
        else:
            pass


    futures_data = pd.read_csv(futures_data_csv_file, header=0)

    return trade_date, futures_data


def get_effr():

    url = r"https://markets.newyorkfed.org/read?productCode=50&eventCodes=500&limit=1&startPosition=0&sort=postDt:-1&format=json"
    response = rq.get(url)
    json_object = response.json()
    json_obj = json.dumps(json_object)
    data = json.loads(json_obj)
    obj_length = len(data['refRates'])

    effr_list = []

    for item in range(obj_length):
        effr_list.append(float(json.dumps(json_object['refRates'][item]['percentRate'])))

    effr = sum(effr_list) / len(effr_list)

    return effr