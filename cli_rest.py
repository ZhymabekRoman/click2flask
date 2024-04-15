from flask import Flask
import click
from loguru import logger
import re
from click.types import StringParamType
from click2flask import register_group

class EmailType(StringParamType):
    name = "email"

    def convert(self, value, param, ctx):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            self.fail(f"{value} is not a valid email address", param, ctx)
        return value


app = Flask(__name__)

cli = click.Group()


@cli.command()
@click.option("-n", "--name", help="Your name", required=True)
@click.option("-s", help="Your burth stree", default="unknown")
@click.option("-cc", help="You from california", is_flag=True, default=False)
@click.option(
    "-v",
    "--verbose",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    default="INFO",
    help="Set the level of verbosity",
)
@click.option("--age", type=int, help="Your age")
def greet(name, age, s, cc, verbose):
    greeting = f"Hello, {name}. You are {age} years old. Your burth street is {s}. You are from California: {cc}. Verbose: {verbose}"
    logger.info(f"Greet command executed with name: {name}, age: {age}")
    click.echo(greeting)
    return greeting


@cli.command()
@click.option("--email", type=EmailType(), help="Your email address", required=True)
def send_email(email):
    message = f"Sending an email to {email}"
    logger.info(message)
    click.echo(message)
    # Here you would implement the logic to send an email
    return {"message": f"Email sent to {email}"}


@cli.command
def exception_text():
    raise Exception("This is an exception")


# Function to register all commands and groups
def register_all():
    register_group(app, cli)


register_all()

if __name__ == "__main__":
    app.run(debug=True)
