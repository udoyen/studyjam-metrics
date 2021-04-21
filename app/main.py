from flask import Flask
from google.cloud import monitoring_v3
import requests
import time

# Google Cloud Monitoring: https://cloud.google.com/monitoring/docs/reference/libraries#command-line

app = Flask(__name__)

# Use this to get the instance metadata
metadata_server = "http://metadata/computeMetadata/v1/instance/"
metadata_flavor = {'Metadata-Flavor' : 'Google'}
gce_id = requests.get(metadata_server + 'id', headers = metadata_flavor).text
gce_name = requests.get(metadata_server + 'hostname', headers = metadata_flavor).text
gce_zone = requests.get(metadata_server + 'zone', headers = metadata_flavor).text

@app.route("/")
def hello():
    client = monitoring_v3.MetricServiceClient()
    project = 'study-jam-deploy'  # TODO: Update to your project ID.
    project_name = f"projects/{project}"

    series = monitoring_v3.TimeSeries()
    series.metric.type = "custom.googleapis.com/studyjam_metric"
    series.resource.type = "gce_instance"
    series.resource.labels["instance_id"] = gce_id
    series.resource.labels["zone"] = gce_zone
    now = time.time()
    seconds = int(now)
    nanos = int((now - seconds) * 10 ** 9)
    interval = monitoring_v3.TimeInterval(
        {"end_time": {"seconds": seconds, "nanos": nanos}}
    )
    point = monitoring_v3.Point({"interval": interval, "value": {"double_value": 3.14}})
    series.points = [point]
    client.create_time_series(request={"name": project_name, "time_series": [series]})
    print("Successfully wrote time series.")
    return "Hello World from Flask"



if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=8080)