import docker


def run_docker_container(image_name, command):
    client = docker.from_env()
    full_command = "/bin/sh -c '" + command + "'"
    try:
        container = client.containers.run(image_name, full_command, detach=True)
        return container

    except docker.errors.ImageNotFound as e:
        raise ValueError(f"Image '{image_name}' not found. Error: {e}")
    except docker.errors.APIError as e:
        raise ValueError(f"API Error: {e}")
    except docker.errors.ContainerError as e:
        raise ValueError(f"Container execution error: {e}")
    except docker.errors.DockerException as e:
        raise ValueError("Connection to the Docker server was refused. Make sure Docker is running.")
    except Exception as e:
        raise ValueError(f"An unexpected error occurred: {e}")
