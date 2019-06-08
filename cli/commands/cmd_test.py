import subprocess

import os


@click.command()
@click.argument('path', default=os.path.join('vidme', 'tests'))
def cli(path):
    """
    Run tests with Pytest. Will test "vidme/tests/" by default

    :param path: Test path
    :return: Subprocess call result
    """
    cmd = 'py.test {0}'.format(path)
    return subprocess.call(cmd, shell=True)