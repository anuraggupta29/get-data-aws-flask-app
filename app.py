from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from data_processing_main import download_data_from_aws, process_data, save_summary_csv

app = Flask(__name__)

arr = []
day, month, year = '','',''

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run_application', methods=['POST'])
def run_application():
    global arr
    global day, month, year

    if request.method == 'POST':
        # Your code to run the application based on the selected date
        print("Running")
        selected_date = request.form['selected_date']
    
        try:
            # Extract day, month, and year 
            selected_date = datetime.strptime(selected_date, "%Y-%m-%d")
            date_format = lambda x: '0'+str(x) if len(str(x))==1 else str(x)
            day = date_format(selected_date.day)
            month = date_format(selected_date.month)
            year = str(selected_date.year)

            main_data_csv_path = r'main_data_{}{}{}.csv'.format(day, month, year)  # Replace with your username
            
            df = download_data_from_aws(day, month, year, main_data_csv_path)

            arr = []
            process_data(df, main_data_csv_path, selected_date, arr)

                
            return "OK"

        except ValueError:
            return "ERROR"
    return "ERROR"

@app.route('/download_data', methods=['GET'])
def download_data():
    global arr
    global day, month, year

    if request.method == 'GET':
        # Your code to download data
        try:
            save_summary_csv(day, month, year, arr)

            # Add your download logic here
            return 'OK'
        except:
            return 'ERROR'
    return 'ERROR'

if __name__ == '__main__':
    app.run(debug=True)
