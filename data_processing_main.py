from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import pandas as pd
import numpy as np
import boto3
import awswrangler as wr

def download_data_from_aws(day, month, year, main_data_csv_path):

    print("Download start : {}".format(datetime.now().strftime("%H:%M:%S")))

    level1_prefix = f'ev_parq_{year}{month}{day}'
    level2_prefix = f'date={year}-{month}-{day}'
    path = f's3://evparqdata/{level1_prefix}/{level2_prefix}/' 
    
    # Add your application logic here
    path = f's3://evparqdata/{level1_prefix}/{level2_prefix}/'  

    columns = ["vin","timestamp_local","vehicle_odo_meter","soc","charging"]
        
    session = boto3.Session(aws_access_key_id="",
    aws_secret_access_key = "")
    
    df = wr.s3.read_parquet(path=path, boto3_session=session, columns=columns)

    print("Download end : {}".format(datetime.now().strftime("%H:%M:%S")))
    
    print("Sorting Start : {}".format(datetime.now().strftime("%H:%M:%S")))
    df_data = df.sort_values(by="timestamp_local", ascending=True)
    print("Sorting end : {}".format(datetime.now().strftime("%H:%M:%S")))

    numrows = df_data.shape[0]
    #print(numrows)

    print("Save as CSV start : {}".format(datetime.now().strftime("%H:%M:%S")))
    # Save the main data to a CSV file on your desktop
    df_data.to_csv(main_data_csv_path, index=False)
    print("Save as CSV end : {}".format(datetime.now().strftime("%H:%M:%S")))
    
    print(main_data_csv_path)


def process_data(df, main_data_csv_path, selected_date, arr):

    print("Processing start : {}".format(datetime.now().strftime("%H:%M:%S")))

    print("read csv start : {}".format(datetime.now().strftime("%H:%M:%S")))
    df1 = pd.read_csv(main_data_csv_path)
    print("read csv end : {}".format(datetime.now().strftime("%H:%M:%S")))

    groups = df1.groupby('vin')
    size = len(groups)
    index = 1

    # Access subsets using keys (unique values)
    for unique_value, subset in groups:
        #print(subset)
        #break

        print("Processing {} / {}".format(index, size))
        index += 1
            
        start_odo = subset.loc[df1['vehicle_odo_meter'].gt(0), 'vehicle_odo_meter'].min()
        end_odo = subset['vehicle_odo_meter'].max()
        km_run = round(end_odo - start_odo,1)
            
        # Find the blocks of 1s in the 'charging' column
        blocks = (subset['charging'] != subset['charging'].shift()).cumsum()
        # Calculate the start and end values for each block of 1s
        soc_starts = subset.loc[df1['charging'] == 1].groupby(blocks)['soc'].first()
        soc_ends = subset.loc[df1['charging'] == 1].groupby(blocks)['soc'].last()
        #print(soc_starts)
        # Calculate the difference between start and end values for each block
        soc_differences = soc_ends - soc_starts
        # Create a new DataFrame with the results
        result_df1 = pd.DataFrame({'Difference': soc_differences})
        soc_charged = result_df1['Difference'].sum()
        
        #Calculating charging time
        time_first = subset.loc[df1['charging'] == 1].groupby(blocks)['timestamp_local'].first()
        time_last = subset.loc[df1['charging'] == 1].groupby(blocks)['timestamp_local'].last()
        time_start = pd.to_datetime(time_first)
        time_end = pd.to_datetime(time_last)
        time_diff = time_end -  time_start
        #print(time_diff)
        # Create a new DataFrame with the results
        result_df2 = pd.DataFrame({'Difference': time_diff})
        time_difference = result_df2 ['Difference'].sum()
        #print(time_difference)
        
        arr.append([selected_date, unique_value, km_run, soc_charged, time_difference])
    
    print("Processing end : {}".format(datetime.now().strftime("%H:%M:%S")))


def save_summary_csv(day, month, year, arr):
    print("create summary start : {}".format(datetime.now().strftime("%H:%M:%S")))
    column_names = ['date', 'vin', 'km_run', 'soc_charged', 'charging_time']
    array = pd.DataFrame(arr, columns=column_names)
    
    file_path2 = r'vin_Bus_code.xlsx'

    # Read the CSV file into a DataFrame
    df2 = pd.read_excel(file_path2)

    mapping1 = df2.set_index('vin')['vehicle_number'].to_dict()
    mapping2 = df2.set_index('vin')['depot'].to_dict()
    mapping3 = df2.set_index('vin')['capacity'].to_dict()

    # Add a new column to df1 using the mapping
    array['vehicle_number'] = array['vin'].map(mapping1)
    array['depot'] = array['vin'].map(mapping2)
    array['kwh_consumption'] = array['vin'].map(mapping3)*array['soc_charged']
    array['efficiency'] = np.where(array['km_run'] == 0, 0, array['kwh_consumption'] / array['km_run'])

    #print(array)
    summary_csv_path = r'summary_data_{}{}{}.csv'.format(day, month, year)  # Replace with your username

    # Save the column headers to a CSV file on your desktop
    array.to_csv(summary_csv_path, index=False)

    print("create summary end : {}".format(datetime.now().strftime("%H:%M:%S")))