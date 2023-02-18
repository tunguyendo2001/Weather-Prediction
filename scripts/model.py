 # -*- coding: utf-8 -*-

import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np # linear algebra
import sys
import os
from os import listdir
from os.path import isfile, join
import tensorflow as tf
import requests
from datetime import datetime, timedelta
import json

from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import *
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.losses import MeanSquaredError
from tensorflow.keras.metrics import RootMeanSquaredError
from tensorflow.keras.optimizers import Adam


pd.set_option('display.max_rows', None)


gateway = "http://localhost:8123"

# predict_time = datetime.now().date() + timedelta(1)
predict_time = datetime.now().date() - timedelta(7)
date_start = predict_time - timedelta(4)

request_body = {
	"zone": "HN",
	"time_start": str(date_start),
	"time_end": str(predict_time - timedelta(1))
}
response = requests.post(gateway + '/search_data', json=request_body)
json_response = response.json()
data = []
for index in json_response['data']:
	data += index
more_data = pd.DataFrame(data)

# processing data
# condition
con_dict = {}
con_list = ['Partly', 'Fair', 'Mostly', 'Cloudy', 'Fog', 'Light', 'Thunder','Heavy', 'T-Storm', 'Rain', 'Haze', 'Smoke', 'Drizzle', 'Patches','in']
for i, v in enumerate(con_list):
	con_dict[v] = i
more_data['condition_value'] = more_data['Condition'].map(con_dict)

# wind direction
pi = np.pi
windir_dict = {
    'SSE':7*pi/8, 
    'ESE': 5*pi/8, 
    'E': pi/2, 
    'SE': 3*pi/4, 
    'VAR':0, 
    'ENE':3*pi/8, 
    'NE': pi/4, 
    'W': 3*pi/2, 
    'NW':7*pi/4, 
    'WNW':13*pi/8,
    'NNW': 15*pi/8, 
    'CALM':0, 
    'N': 2 * pi, 
    'S': pi, 
    'NNE': pi/8, 
    'SSW':9*pi/8, 
    'WSW':11*pi/8, 
    'SW':5*pi/4, 
    '0' : 0,
}
more_data['wind_value'] = more_data['Wind(Direction)'].map(windir_dict)

# temperature
more_data['temperature_value'] = more_data['Temperature(\u00b0F)'].astype(int)
more_data['temperature_celsius'] = (more_data["Temperature(\u00b0F)"] - 32) * 5 /9

# humidity
more_data['humidity_value'] = more_data['Humidity(%)'].astype(int)/100

# wind speed
more_data['wind_speed_value'] = more_data['Wind Speed(mph)'].astype(int)

# presure
more_data['presure_value'] = more_data['Presure(in)'].astype(float)

# date time
more_data['date_time'] = more_data['Timestamp'].apply(lambda x: datetime.fromtimestamp(x))


# create temperature dataframe
tmp_df = pd.DataFrame({'Temperature':more_data['temperature_value']})
tmp_df["humidity_value"] = more_data["humidity_value"]
tmp_df["wind_speed_value"] = more_data["wind_speed_value"]
tmp_df["wind_value"] = more_data["wind_value"]
tmp_df["presure_value"] = more_data["presure_value"]
tmp_df["condition_value"] = more_data["condition_value"]

tmp_df.index = pd.to_datetime(more_data['date_time'])
tmp_df['Seconds'] = tmp_df.index.map(pd.Timestamp.timestamp)
day = 60*60*24
year = 365.2425*day
tmp_df['Day sin'] = np.sin(tmp_df['Seconds'] * (2* np.pi / day))
tmp_df['Day cos'] = np.cos(tmp_df['Seconds'] * (2 * np.pi / day))
tmp_df['Year sin'] = np.sin(tmp_df['Seconds'] * (2 * np.pi / year))
tmp_df['Year cos'] = np.cos(tmp_df['Seconds'] * (2 * np.pi / year))
tmp_df = tmp_df.drop('Seconds', axis=1)
full_temp_df = tmp_df.copy()

def df_to_X_y_temp(df, window_size_x=5, window_size_y=5):
	df_as_np = df.to_numpy()
	X = []
	y = []
	for i in range(len(df_as_np)-window_size_y-window_size_x-1):
		row = [a for a in df_as_np[i:i+window_size_x]]
		X.append(row)
		label = df_as_np[i+window_size_x+1:i+window_size_x+1+window_size_y][:,0]
		y.append(label)
	return np.array(X), np.array(y)

def convert_to_input_format(df, window_size_x=5, window_size_y=5):
	df_as_np = df.to_numpy()
	X = []
	row = [a for a in df_as_np[:window_size_x]]
	X.append(row)
	
	return np.array(X)

WINDOW_SIZEx = 48 * 4
WINDOW_SIZEy = 48

X1 = convert_to_input_format(full_temp_df, WINDOW_SIZEx, WINDOW_SIZEy)
# print(X1.shape)

temp_training_mean = np.mean(X1[:, :, 0])
temp_training_std = np.std(X1[:, :, 0])
# presure_training_mean = np.mean(X_train1[:, :, 8])
# presure_training_std = np.std(X_train1[:, :, 8])
                           
def preprocess(X):
	X[:, :, 0] = (X[:, :, 0] - temp_training_mean) / temp_training_std
	# X[:, :, 8] = (X[:, :, 8] - presure_training_mean) / presure_training_std
	return X

# # define model with GRU cell
# model = Sequential()
# model.add(InputLayer((WINDOW_SIZEx, X_train1.shape[-1])))
# # model.add(LSTM(64))
# model.add(GRU(64))
# # model.add(Dropout(0.05))
# model.add(Dense(8, 'relu'))
# model.add(Dense(WINDOW_SIZEy, 'linear'))

last_checkpoint = sys.argv[1]
new_model = load_model(last_checkpoint)
# cp = ModelCheckpoint(last_checkpoint, save_best_only=True)
# new_model.fit(X_train1, y_train1, validation_data=(X_val1, y_val1), epochs=1, callbacks=[cp])

# print("X1: ", X1)
X = preprocess(X1)
X_predict = new_model.predict(X)*temp_training_std + temp_training_mean
f = open('../predictions/pred'+str(predict_time), 'w')
for res in X_predict[0]:
	print(res, file=f)
f.close()
























