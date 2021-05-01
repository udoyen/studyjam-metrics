### Study Jam Project

### Note:

Steps to run on your vm instances:

1. Create a service and grant it access to Metric writing for the VM instance


Steps to create a custom metrics

1. Import the Google Monitoring Library
2. Create a metric descriptor
3. Create a data point
4. Create a time series 
5. Write request object => write!


Monitoring API

- Format: "custom.google.com/[global | <resource_type>]/<custom_metric_name>
- Info:
   - global: generic use
   - resource_type: specific resource use

### Beginner Guide

Link: https://medium.com/google-cloud/stackdriver-custom-metrics-in-python-30fafb585a1d


### Run project

1. Create a virtualenv
2. Install dependencies from requirements.txt file
3. Activate the environment
4. If using ```pyenv``` run ```pipenv install``` from the app folder