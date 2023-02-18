for pid in $(ps -ef | grep "logstash" | awk '{print $2}'); do kill $pid; done
