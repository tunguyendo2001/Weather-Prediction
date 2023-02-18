cd /Users/hadoop/Downloads/ds-proj/data/
filename=$(ls -t *.csv | head -1)
csv=/Users/hadoop/Downloads/ds-proj/data/$filename
index=${filename:0:12}
index="$(tr [A-Z] [a-z] <<< "$index")"
if [ ! -f /Users/hadoop/Downloads/ds-proj/ds-logstash-config/config-$index.conf ]; then
echo "input {
    file {
        path => \"$csv\"
        start_position => \"beginning\"
        sincedb_path => \"/tmp/null\"
    }
}
filter {
    csv {
        separator => \",\"
        skip_header => \"true\"
        columns => [\"Hour\",\"Temperature(°F)\",\"Dew Point(°F)\",\"Humidity(%)\",\"Wind(Direction)\",\"Wind Speed(mph)\",\"Wind Gust(mph)\",\"Presure(in)\",\"presip\",\"Condition\",\"Year\",\"Month\",\"Date\",\"Timestamp\"]
    }
    mutate {convert => {\"Timestamp\" => \"float\"}}
    mutate {convert => {\"Year\" => \"integer\"}}
    mutate {convert => {\"Month\" => \"integer\"}}
    mutate {convert => {\"Date\" => \"integer\"}}
    mutate {convert => {\"Temperature(°F)\" => \"float\"}}
    mutate {convert => {\"Dew Point(°F)\" => \"float\"}}
    mutate {convert => {\"Humidity(%)\" => \"float\"}}
    mutate {convert => {\"Presure(in)\" => \"float\"}}
    mutate {convert => {\"Wind Speed(mph)\" => \"float\"}}
}
output {
    elasticsearch {
        hosts => \"http://localhost:9200\"
        index => \"$index\"
    }
    exec {
        command => \"sh /Users/hadoop/Downloads/ds-proj/scripts/kill_logstash.sh && exit 0\"
    }
stdout {}
}" >> /Users/hadoop/Downloads/ds-proj/ds-logstash-config/config-$index.conf;
else
rm /Users/hadoop/Downloads/ds-proj/ds-logstash-config/config-$index.conf
echo "input {
    file {
        path => \"$csv\"
        start_position => \"beginning\"
        sincedb_path => \"/tmp/null\"
    }
}
filter {
    csv {
        separator => \",\"
        skip_header => \"true\"
        columns => [\"Hour\",\"Temperature(°F)\",\"Dew Point(°F)\",\"Humidity(%)\",\"Wind(Direction)\",\"Wind Speed(mph)\",\"Wind Gust(mph)\",\"Presure(in)\",\"presip\",\"Condition\",\"Year\",\"Month\",\"Date\",\"Timestamp\"]
    }
    mutate {convert => {\"Timestamp\" => \"float\"}}
    mutate {convert => {\"Year\" => \"integer\"}}
    mutate {convert => {\"Month\" => \"integer\"}}
    mutate {convert => {\"Date\" => \"integer\"}}
    mutate {convert => {\"Temperature(°F)\" => \"float\"}}
    mutate {convert => {\"Dew Point(°F)\" => \"float\"}}
    mutate {convert => {\"Humidity(%)\" => \"float\"}}
    mutate {convert => {\"Presure(in)\" => \"float\"}}
    mutate {convert => {\"Wind Speed(mph)\" => \"float\"}}
}
output {
    elasticsearch {
        hosts => \"http://localhost:9200\"
        index => \"$index\"
    }
    exec {
        command => \"sh /Users/hadoop/Downloads/ds-proj/scripts/kill_logstash.sh && exit 0\"
    }
stdout {}
}" >> /Users/hadoop/Downloads/ds-proj/ds-logstash-config/config-$index.conf;
fi
