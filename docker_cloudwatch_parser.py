import argparse
import sys

def parse_args():
    parser = argparse.ArgumentParser(description="Run a Docker container and stream logs to AWS CloudWatch.")
    parser.add_argument("--docker-image", required=True, help="Name of the Docker image")
    parser.add_argument("--bash-command", required=True, help="Bash command to run inside the Docker image")
    parser.add_argument("--aws-cloudwatch-group", required=True, help="Name of the AWS CloudWatch log group")
    parser.add_argument("--aws-cloudwatch-stream", required=True, help="Name of the AWS CloudWatch log stream")
    parser.add_argument("--aws-access-key-id", required=True, help="AWS Access Key ID")
    parser.add_argument("--aws-secret-access-key", required=True, help="AWS Secret Access Key")
    parser.add_argument("--aws-region", required=True, help="Name of the AWS region")
    
    try:
        args = parser.parse_args()
        return args
    
    except argparse.ArgumentError as e:
        parser.error(str(e))

    except Exception as e:
        print(f"An error occurred while parsing arguments: {e}", file=sys.stderr)
        sys.exit(1)
