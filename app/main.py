import requests
import uuid
import ssl
import time
from flask import Flask
from google.cloud import monitoring_v3
from google.cloud import secretmanager
from google.cloud import storage
from threading import Thread

# Google Cloud Monitoring: https://cloud.google.com/monitoring/docs/reference/libraries#command-line

app = Flask(__name__)

# Create a global HTTP session (which provides connection pooling)
session = requests.Session()

def gcp_api_call(request, count=0):
    """
    HTTP Cloud Function that uses a connection pool to make HTTP requests.
    Args:
        request (flask.Request): The request object.
        <http://flask.pocoo.org/docs/1.0/api/#flask.Request>
        count: The count metric
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>.
    """
    try:
        # The URL to send the request to
        # url = 'http://example.com'

        # Process the request
        # response = session.get(url)
        # response.raise_for_status()
        # Use this to get the instance metadata
        # metadata_server = "http://metadata/computeMetadata/v1/instance/"
        metadata_server = "http://metadata.google.internal/computeMetadata/v1/instance/"

        metadata_server_for_project = "http://metadata.google.internal/computeMetadata/v1/project/"

        metadata_flavor = {'Metadata-Flavor' : 'Google'}
        with request as s:
            gce_id = s.get(metadata_server + 'id', headers = metadata_flavor).text
            gce_name = s.get(metadata_server + 'hostname', headers = metadata_flavor).text
            gce_zone = s.get(metadata_server + 'zone', headers = metadata_flavor).text
            gce_project_id = request.get(metadata_server_for_project + 'project-id', headers = metadata_flavor).text

        # INFO: This returns the zone of the instance
        zone = gce_zone[gce_zone.index('z')::][gce_zone[gce_zone.index('z')::].index('/') + 1::]

        #INFO: Create the metric client
        metricClient = monitoring_v3.MetricServiceClient()
        project = gce_project_id  # TODO: Update to your project ID.
        project_name = f"projects/{project}"

        #INFO: Setup the time series
        series = monitoring_v3.TimeSeries()
        series.metric.type = "custom.googleapis.com/studyjam_metric"
        series.resource.type = "gce_instance"
        series.resource.labels["instance_id"] = gce_id
        series.resource.labels["zone"] = zone

        now = time.time()
        seconds = int(now)
        nanos = int((now - seconds) * 10 ** 9)
        interval = monitoring_v3.TimeInterval(
            {"end_time": {"seconds": seconds, "nanos": nanos}}
        )

        #INFO: Create the data point
        point = monitoring_v3.Point({"interval": interval, "value": {"double_value": count}})
        print(f"Count: {count}")
        series.points = [point]

        #INFO: Write 
        metricClient.create_time_series(request={"name": f"projects/{gce_project_id}/gce_instance/{gce_id}", "time_series": [series]})

        print("Successfully wrote time series.")

        return 'Success!'
    except Exception as e:
        print(f"The time series wasn't written: {e}")
        return 'Failure'


secret_id = 'metric-secret'
# Create the Secret Manager client.
secretClient = secretmanager.SecretManagerServiceClient()
version_id = 1

def get_secret(project_id, secret_id, version_id="latest"):
    # projects/153702000616/secrets/metric-secret/versions/1
    # Build the resource name of the secret version.
    name = f"projects/steam-kingdom-311415/secrets/{secret_id}/versions/{version_id}"
    # Access the secret version
    response = secretClient.access_secret_version(request={"name" : name})
    secret = response.payload.data.decode("UTF-8")
    print("Plaintext: {}".format(secret))

# get_secret(project_id="steam-kingdom-311415", secret_id=secret_id, version_id=1)

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    try:
        storage_client = storage.Client()

        bucket = storage_client.bucket(bucket_name)

        # Construct a client side representation of a blob.
        # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
        # any content from Google Cloud Storage. As we don't need additional data,
        # using `Bucket.blob` is preferred here.
        blob = bucket.blob(source_blob_name)
        blob.download_to_filename(destination_file_name)

        print(
            "Blob {} downloaded to {}.".format(
                source_blob_name, destination_file_name
            )
        )
    except Exception as e:
        print(f"Error: {e}")

# INFO: Retrieve the crt files from cloud storage
download_blob('study-jam-keys', 'keys/local.crt', './local2.crt')
download_blob('study-jam-keys', 'keys/local.key', './local2.key')

    
@app.route("/")
def hello():
    """Flask hello function

    Returns:
        String: Returns a simple string
    """
    # get_secret('steam-kingdom-311415')
    # write_to_monitoring()
    monitor = TestThreading()
    return "Hello World from Flask"


@app.route("/studyjam")
def welcome():
    """Flask welcome function

    Returns:
        String: Returns a simple string
    """
    # get_secret('steam-kingdom-311415')
    # write_to_monitoring()
    # monitor = TestThreading()
    return "Welcome to Studyjam Flask"

class TestThreading(object):
    """Class used to run the monitoring writes 
    in the background

    Args:
        object (class): [description]
    """
    def __init__(self, interval=5):
        self.interval = interval
        thread = Thread(target=self.write_to_monitoring, args=())
        thread.daemon = True
        thread.start()
    def write_to_monitoring(self):
        count = 1
        for i in range(50):
            time.sleep(5)
            gcp_api_call(session, count=count)
            count += 1


if __name__ == "__main__":
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('./local2.crt', './local2.key')
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=8080, ssl_context=context)