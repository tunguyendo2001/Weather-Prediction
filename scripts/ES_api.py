import json
from datetime import datetime, timedelta
import pandas

from elasticsearch import Elasticsearch
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

es = Elasticsearch("http://localhost:9200")
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

port = 8123

@app.route('/')
def index():
	return f"DS server is running {port}\n"

@app.route('/ping', methods=['GET'])
def ping():
	return "pong\n"

'''
	request body:
	{
		"zone": "HN",
		"time_start": "2023-02-07",
		"time_end": "2023-02-10"
	}
	curl -X POST http://localhost:8123/data_search -H "Content-Type: application/json" -d '{"zone": "HN","time_start": "2023-02-07","time_end": "2023-02-10"}'
'''
@app.route('/search_data', methods=['POST'])
async def request_data():
	try:
		req_data = json.loads(request.data)
		start_date = datetime.strptime(req_data['time_start'], "%Y-%m-%d")
		end_date = datetime.strptime(req_data['time_end'], "%Y-%m-%d")

		date_requests = pandas.date_range(start_date, end_date, freq='d').strftime('%Y-%m-%d').tolist()
		es_indexes = [req_data['zone'].lower()+x for x in date_requests]
		data = []
		for index in es_indexes:
			_data_hits = es.search(
				index=index,
				body={
				  	"size": 50, 
				  	"sort": [
				    {
				      	"Timestamp": {
				        	"order": "asc"
				      	}
				    }
				  	],
				  	"_source": ["Hour","Temperature(°F)","Dew Point(°F)","Humidity(%)","Wind(Direction)","Wind Speed(mph)","Wind Gust(mph)","Presure(in)","presip","Condition","Year","Month","Date","Timestamp"],
				  	"query": {
				    	"match_all": {}
				  	}
				}
			)
			data.append([x["_source"] for x in _data_hits['hits']['hits']])

		return jsonify({
			"status": 200,
			"time_start": start_date.strftime('%Y-%m-%d'),
			"time_end": end_date.strftime('%Y-%m-%d'),
			# "time_requests": date_requests,
			# "es_indexes": es_indexes
			"data": data
		})
	except Exception as e:
		return jsonify({
			"status": 400,
			"ERROR": e
		})


'''
	request body;
	{
		"date": "2023-02-12"
	}
	response: {
		"status": 200,
		"data": [a, b, c, ...] => nhiet do cua ngay "2023-02-13" theo gio, thu tu lan luot 00:00, 00:30, 01:00, ... (len=48)
	}
'''
@app.route('/predict_results', methods=['POST'])
async def get_prediction():
	try:
		req_data = json.loads(request.data)
		predict_date = req_data['date']
		print('Prediction file: ', 'pred'+predict_date)
		prediction_file = open('../predictions/pred'+predict_date, 'r')
		results = prediction_file.readlines()
		return jsonify({
			"status": 200,
			"data": results
		})

	except Exception as e:
		return jsonify({
			"status": 400,
			"ERROR": e
		})


if __name__ == "__main__":
	app.run(debug=True, host='localhost', port=port)
