from datetime import datetime, timedelta
import pytz
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
	'owner': 'tund',
	'retries': 0,
	'retry_delay': timedelta(minutes=1)
}

with DAG(
	dag_id='ds_weather_prediction_module',
	description='This is auto crawler tool to grab weather data in wunderground.com',
	default_args=default_args,
	start_date=datetime(2023, 2, 12, 23, 59, 0, 0, pytz.timezone("Asia/Ho_Chi_Minh")),
	schedule='59 23 * * *'
) as dag:
	# normalize = BashOperator(
	# 	task_id='normalize_data',
	# 	bash_command="source /Users/hadoop/Downloads/ds-proj/ds/bin/activate && cd /Users/hadoop/Downloads/ds-proj/data/ && python /Users/hadoop/Downloads/ds-proj/scripts/normalize_data.py $(ls -t *.csv | head -1)"
	# )

	# crawl = BashOperator(
	# 	task_id='crawling_data',
	# 	bash_command="source /Users/hadoop/Downloads/ds-proj/ds/bin/activate && python /Users/hadoop/Downloads/ds-proj/scripts/crawler.py"
	# )

	# insert2ES = BashOperator(
	# 	task_id='insert_data_ES',
	# 	bash_command="sh /Users/hadoop/Downloads/ds-proj/scripts/ds_elk_script.sh && cd /Users/hadoop/Downloads/ds-proj/ds-logstash-config/ && logstash -f $(ls -t *.conf | head -1)"
	# )

	prediction = BashOperator(
		task_id='prediction',
		bash_command="source /Users/hadoop/Downloads/ds-proj/ds/bin/activate && cd /Users/hadoop/Downloads/ds-proj/checkpoint/ && echo $(ls -td model* | head -1) && python /Users/hadoop/Downloads/ds-proj/scripts/model.py $(ls -td model* | head -1)"
	)

	prediction
