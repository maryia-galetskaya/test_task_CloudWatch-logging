from cloudwatch_managers import LogStreamer, create_cloudwatch_client, create_cloudwatch_log_group, create_cloudwatch_log_stream
from docker_cloudwatch_parser import parse_args
from docker_manager import run_docker_container


def main():
    args = parse_args()
    
    cloudwatch_client = create_cloudwatch_client(
        aws_access_key_id=args.aws_access_key_id,
        aws_secret_access_key=args.aws_secret_access_key,
        region_name=args.aws_region
    )

    create_cloudwatch_log_group(cloudwatch_client, args.aws_cloudwatch_group)
    create_cloudwatch_log_stream(cloudwatch_client, args.aws_cloudwatch_group, args.aws_cloudwatch_stream)

    container = run_docker_container(args.docker_image, args.bash_command)

    print('Docker container is created. It is running.')
    log_streamer = LogStreamer(cloudwatch_client, args.aws_cloudwatch_group, args.aws_cloudwatch_stream)

    try:
        log_streamer.stream_logs_to_cloudwatch(container)
    except KeyboardInterrupt:
        print('Interrupted by user, sending remaining logs...')
        log_streamer.send_log_events()
    finally:
        container.stop()

    print('Everything is successfull.')

if __name__ == "__main__":
    main()