# Docker to CloudWatch Logging Utility

This utility streams logs from a Docker container to AWS CloudWatch, providing an integrated solution for managing container logs. It automates the creation of CloudWatch log groups and streams and handles log shipping.


## Features

**Docker Container Management:** Runs a Docker container based on specified image and command arguments.

**AWS CloudWatch Integration:** Automatically creates log groups and streams in AWS CloudWatch and streams logs in real-time.

**Error Handling:** Implements robust error handling for AWS service interactions.

**Graceful Shutdown:** Captures interrupt signals to ensure all remaining logs are sent to CloudWatch before the program exits.



## Prerequisites
- Docker installed and running on your machine.
- AWS CLI installed and configured with appropriate credentials.
- Python 3.6+ and pip for installing dependencies.


## Installation

### 1. Clone the repository to your local machine:
```
git clone https://github.com/maryia-galetskaya/test_task_CloudWatch-logging.git
```
```
cd test_task_CloudWatch-logging
```

### 2. Set Up a Virtual Environment
Create and activate a virtual environment to manage the project's Python dependencies independently from your global Python environment.

For macOS/Linux:
```
python3 -m venv venv
source venv/bin/activate
```

For Windows:
```
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install required Python dependencies:

    ```
    pip install -r requirements.txt
    ```

    This script requires *boto3* and *docker* Python packages.

## Configuration

Before running the script, ensure your IAM user has the necessary permissions. The script requires the following AWS permissions:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
```

## Usage

Run the script with the necessary arguments:

```
python main.py --docker-image python --bash-command $'pip install pip -U && pip install tqdm && python -c \"import time\ncounter = 0\nwhile True:\n\tprint(counter)\n\tcounter = counter + 1\n\ttime.sleep(0.1)\"' --aws-cloudwatch-group test-task-group-1 --aws-cloudwatch-stream test-task-stream-1 --aws-access-key-id <AWS-ACCESS-KEY> --aws-secret-access-key <AWS-SECRET-ACCESS-KEY> --aws-region <AWS-REGION>
```




- The script is designed to handle __*KeyboardInterrupt*__ `(Ctrl+C)` gracefully, ensuring that any logs generated up to the point of interruption are sent to `CloudWatch` before the program exits.

- You can customize **the batch size limit** and other parameters by modifying the `LogStreamer` class within `cloudwatch_managers.py`.
