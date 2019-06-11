import click

from vidme.app import create_app

app = create_app()


@click.command()
def cli():
    """
    List all of the applicaion routes.

    :return: str
    """
    output = {}

    for rule in app.url_map.iter_rules():
        route = {
            'path': rule.rule,
            'methods': '({0})'.format(', '.join(rule.methods))
        }

        output[rule.endpoint] = route

    # add padding
    padding = max(len(endpoint) for endpoint in output.keys()) + 2
    
    # sort the routes then print each
    for key in sorted(output):
        click.echo('{0: >{1}}: {2}'.format(key, padding, output[key]))
