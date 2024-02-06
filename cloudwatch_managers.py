import datetime
from functools import wraps
import boto3
import botocore


def handle_aws_errors(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        try:
            return method(*args, **kwargs)
        
        except botocore.exceptions.NoCredentialsError:
            raise ValueError("AWS credentials are missing. Please provide valid access key and secret access key.")
        
        except botocore.exceptions.EndpointConnectionError as e:
            raise ValueError(f"Unable to connect to AWS endpoint: {e}")
        
        except botocore.exceptions.ClientError as e:
            error_message = str(e)
            if "AccessDenied" in error_message:
                raise ValueError(f"Access denied while interacting with AWS: {e}")
            elif "Throttling" in error_message:
                raise ValueError(f"AWS API throttling error: {e}")
            else:
                raise ValueError(f"An error occurred while interacting with AWS: {e}")

    return wrapper


@handle_aws_errors
def create_cloudwatch_client(aws_access_key_id, aws_secret_access_key, region_name):
    client = boto3.client(
        'logs', 
        aws_access_key_id=aws_access_key_id, 
        aws_secret_access_key=aws_secret_access_key, 
        region_name=region_name
    )
    print('Cloudwatchclient is created.')
    return client


@handle_aws_errors
def create_cloudwatch_log_group(client, log_group_name):

    response = client.describe_log_groups(logGroupNamePrefix=log_group_name)
    log_groups = response.get('logGroups', [])
    if not any(log_group['logGroupName'] == log_group_name for log_group in log_groups):
        client.create_log_group(logGroupName=log_group_name)
        print(f"Log group '{log_group_name}' is created")
    else:
        print(f"Log group '{log_group_name}' already exists. Skipping creation.")


@handle_aws_errors
def create_cloudwatch_log_stream(client, log_group_name, log_stream_name):
    response = client.describe_log_streams(
        logGroupName=log_group_name,
        logStreamNamePrefix=log_stream_name
    )
    log_streams = response.get('logStreams', [])
    if not any(log_stream['logStreamName'] == log_stream_name for log_stream in log_streams):
        client.create_log_stream(logGroupName=log_group_name, logStreamName=log_stream_name)
        print(f"Log stream '{log_stream_name}' is created")
    else:
        print(f"Log stream '{log_stream_name}' already exists. Continuing with existing log stream.")


class LogStreamer:
    def __init__(self, cloudwatch_client, log_group_name, log_stream_name):
        self.cloudwatch_client = cloudwatch_client
        self.log_group_name = log_group_name
        self.log_stream_name = log_stream_name
        self.log_events_batch = []
        self.sequence_token = None
        self.batch_size_limit = 1000

    @handle_aws_errors
    def fetch_sequence_token(self):
        response = self.cloudwatch_client.describe_log_streams(
            logGroupName=self.log_group_name,
            logStreamNamePrefix=self.log_stream_name
        )
        streams = response['logStreams']
        if streams:
            self.sequence_token = streams[0].get('uploadSequenceToken')

    @handle_aws_errors
    def add_log_event(self, log):
        log_event = {
            'timestamp': int(datetime.datetime.now().timestamp() * 1000),
            'message': log.decode().strip()
        }
        self.log_events_batch.append(log_event)

        if len(self.log_events_batch) >= self.batch_size_limit:
            self.send_log_events()

    @handle_aws_errors
    def send_log_events(self):
        if not self.log_events_batch:
            return

        print('Sending logs to CloudWatch...')
        try:
            params = {
                'logGroupName': self.log_group_name,
                'logStreamName': self.log_stream_name,
                'logEvents': self.log_events_batch
            }
            if self.sequence_token:
                params['sequenceToken'] = self.sequence_token
            response = self.cloudwatch_client.put_log_events(**params)
            self.sequence_token = response.get('nextSequenceToken')
            self.log_events_batch = []
        except botocore.exceptions.ClientError as e:
            print(f"Error sending log events: {e}")
            if e.response['Error']['Code'] == 'InvalidSequenceTokenException':
                self.sequence_token = e.response['Error']['Message'].split(' ')[-1]
                self.send_log_events()
        except Exception as e:
            print(f"Unexpected error: {e}")

    @handle_aws_errors
    def stream_logs_to_cloudwatch(self, container):
        self.fetch_sequence_token()
        for log in container.logs(stream=True):
            self.add_log_event(log)
        self.send_log_events()