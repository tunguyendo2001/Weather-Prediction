import pandas as pd
import sys
import re
from datetime import datetime

data_folder = "/Users/hadoop/Downloads/ds-proj/data/"
filename = sys.argv[1]

list_data = []
try:
    df = pd.read_csv(data_folder+filename, index_col=None, names=["hour", "temperature", "dew_point", "humidity", "wind", "wind_speed", "wind_gust", "presure", "presip", "condition"])
    year, month, date = filename[:-4].split('-')
    year = year[-4:]
    df['year'] = [year]*df.shape[0]
    df['month'] = [month]*df.shape[0]
    df['date'] = [date]*df.shape[0]
    list_data.append(df)
except pd.errors.EmptyDataError:
    print(filename + "is empty or not existed !!!")
    pass

df_data = pd.concat(list_data, axis=0, ignore_index=True)
_df_data = df_data.copy()

# convert data type
try:
    _df_data['temperature'] = _df_data['temperature'].apply(lambda x: float(re.findall("\d+", x)[0]))
    _df_data['dew_point'] = _df_data['dew_point'].apply(lambda x: float(re.findall("\d+", x)[0]))
    _df_data['humidity'] = _df_data['humidity'].apply(lambda x: float(re.findall("\d+", x)[0]))

    # _df_data['wind_speed'] = _df_data['wind_speed'].apply(lambda x: float(x[:-4]))
    _df_data['wind_speed'] = _df_data['wind_speed'].apply(lambda x: float(re.findall("\d+", x)[0]))

    _df_data['wind_gust'] = _df_data['wind_gust'].apply(lambda x: float(re.findall("\d+", x)[0]))
    _df_data['presure'] = _df_data['presure'].apply(lambda x: float(x[:-3]))
    _df_data['year'] = _df_data['year'].apply(lambda x: int(x))
    _df_data['month'] = _df_data['month'].apply(lambda x: int(x))
    _df_data['date'] = _df_data['date'].apply(lambda x: int(x))
except Exception as e:
    print("ERROR: ", e)
    pass

def convert_hour(x):
    try:
        if 'PM' in x and '12' not in x:
            _x = x[:-3].split(':')
            return str(int(_x[0]) + 12) + ':' + _x[1]
        elif '12' in x and 'AM' in x:
            _x = x[:-3].split(':')
            return '00:' + _x[1]
        return x[:-3]
    except:
        print(x)
_df_data['hour'] = _df_data['hour'].apply(lambda x: convert_hour(x))

# change name
_df_data = _df_data.rename(columns={
    'hour': "Hour",
    'temperature': "Temperature(°F)",
    'dew_point': "Dew Point(°F)",
    'humidity': "Humidity(%)",
    'wind': "Wind(Direction)",
    'wind_speed': "Wind Speed(mph)",
    'wind_gust': 'Wind Gust(mph)',
    'presure': "Presure(in)",
    'condition': "Condition",
    'year': "Year",
    'month': "Month",
    'date': "Date"
})
timestamp = []
for i in range(len(_df_data)):
    timestp = str(_df_data['Date'][i]) + '.' + str(_df_data['Month'][i]) + '.' + str(_df_data['Year'][i]) + ' ' + _df_data['Hour'][i]
    d = datetime.strptime(timestp, "%d.%m.%Y %H:%M").strftime('%s.%f')
    d_in_ms = int(float(d))
    timestamp.append(d_in_ms)

_df_data['Timestamp'] = timestamp

_df_data.to_csv(data_folder+filename, index=False)

