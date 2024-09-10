#!/usr/bin/env python

import os
import sys
import argparse
import webbrowser

CWD = os.getcwd()


# ----------------------------------------------------------------------
def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments for Docker Sphinx Documentation Helper.

    This function uses argparse to parse command-line arguments intended for Docker commands.
    The function expects arguments for commands, including the command itself, module or directory,
    and format or port details.

    Returns
    -------
    argparse.Namespace
        An object containing the parsed command-line arguments.

    Example
    -------
    >>> args = parse_arguments()
    >>> print(args.args)
    """
    parser = argparse.ArgumentParser(
        description='Docker Sphinx Documentation Helper')
    parser.add_argument(
        'args', nargs='*', help='Arguments for commands: [command, module/dir, format/port]')
    return parser.parse_args()


# ----------------------------------------------------------------------
def run_docker_command(image: str, command: str, volumes: str, arguments: str = '') -> None:
    """
    Execute a Docker command with specified parameters.

    This function runs a Docker command using the os.system call. It takes the Docker image name,
    the command to execute, and volume mappings as inputs.

    Parameters
    ----------
    image : str
        The name of the Docker image to use.
    command : str
        The Docker command to be executed.
    volumes : str
        The volume mappings for the Docker command.

    Example
    -------
    >>> run_docker_command("python:3.8", "echo Hello, World!", "/myhostpath:/mycontainerpath")
    """

    instruction = f"docker run --rm -u $(id -u):$(id -g) {volumes} {image} {command} {arguments}"
    print(f'Running: {instruction}')
    os.system(instruction)


# ----------------------------------------------------------------------
def main():
    """
    Main function to handle Docker commands for Sphinx documentation.

    Parses arguments from the command line and executes corresponding Docker commands based
    on the provided input. Supported commands include 'quickstart', 'apidoc', 'build', and 'server'.
    """
    args = parse_arguments().args

    if not args:
        print("No command provided.")
        return

    command = args[0]
    image = 'dunderlab/docs:latest'

    try:
        if not os.path.exists('docs'):
            os.mkdir('docs')

        if command == 'quickstart':
            try:
                args = parse_arguments().args
                arguments = args[1]
            except:
                arguments = ''
            run_docker_command(image, 'sphinx-quickstart',
                               f'-v {CWD}/docs:/mnt/docs -w /mnt/docs', arguments=arguments)

        elif command == 'apidoc':
            try:
                args = parse_arguments().args
                apidoc_options = args[2]
            except:
                apidoc_options = 'members,undoc-members,show-inheritance'
            handle_apidoc_command(args, image, apidoc_options)

        elif command == 'build':
            handle_build_command(args, image)

        elif command == 'server':
            handle_server_command(args)

    except Exception as e:
        print(f"An error occurred: {e}")


# ----------------------------------------------------------------------
def handle_apidoc_command(args: list[str], image: str, apidoc_options: str = '') -> None:
    """
    Handle 'apidoc' command for Sphinx documentation.

    Parameters
    ----------
    args : list[str]
        List of arguments passed from the command line.
    image : str
        Docker image to use for running the command.
    """
    if len(args) > 1:
        module = args[1]
        run_docker_command(
            image,
            f'sphinx-apidoc -fMeETl -t source/_templates -o source/_modules ../{module}',
            f"-v {CWD}/docs:/mnt/docs -v {CWD}:/mnt -w /mnt/docs -e SPHINX_APIDOC_OPTIONS='{apidoc_options}'",
        )
    else:
        print('Module name must be specified for apidoc.')


# ----------------------------------------------------------------------
def handle_build_command(args: list[str], image: str) -> None:
    """
    Handle 'build' command for Sphinx documentation.

    Parameters
    ----------
    args : list[str]
        List of arguments passed from the command line.
    image : str
        Docker image to use for running the command.
    """
    if len(args) > 2:
        format_, module = args[1], args[2]
        if format_ in ['html', 'epub', 'latexpdf', 'clean']:
            run_docker_command(
                image, f'make {format_}', f'-v {CWD}:/mnt -w /mnt/docs')
        else:
            print('Invalid output format specified for build.')
    else:
        print('Module name and output format must be specified for build.')


# ----------------------------------------------------------------------
def handle_server_command(args: list[str]) -> None:
    """
    Handle 'server' command to launch a local server for Sphinx documentation.

    Parameters
    ----------
    args : list[str]
        List of arguments passed from the command line.
    """
    if len(args) > 1:
        port = args[1]
        os.chdir(os.path.join('docs', 'build', 'html'))
        webbrowser.open_new_tab(f'http://localhost:{port}/index.html')
        os.system(f"python -m http.server {port}")
    else:
        print('Port number must be specified for server.')


if __name__ == '__main__':
    main()

