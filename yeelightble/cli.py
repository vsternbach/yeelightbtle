import asyncio
import logging
import click
import sys

from .btle import BTLEScanner
from .lamp import Lamp
from .server import Server
from .version import __version__

pass_dev = click.make_pass_decorator(Lamp)
logger = logging.getLogger(__name__)


@click.group(invoke_without_command=True)
@click.option('--mac', envvar="YEELIGHTBLE_MAC", required=False)
@click.option('-d', '--debug', default=False, count=True)
@click.pass_context
def cli(ctx, mac, debug):
    """ A tool to interact with Yeelight Candela/Bedside Lamp. Will run as a daemon if no arguments were passed."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(format='%(asctime)s %(levelname)s [%(name)s] %(message)s', level=level)
    # if we are scanning, we do not need to connect.
    if ctx.invoked_subcommand in ("scan", "daemon"):
        return

    if ctx.invoked_subcommand is None:
        ctx.invoke(daemon)
        return

    if mac is None:
        logger.error("mac address is missing, set YEELIGHTBLE_MAC environment variable or pass --mac option")
        sys.exit(1)

    ctx.obj = Lamp(mac)


@cli.command()
@click.option('--host', envvar="YEELIGHTBLE_HOST", default="0.0.0.0", show_default=True)
@click.option('--port', envvar="YEELIGHTBLE_PORT", default=8765, show_default=True)
def daemon(host, port):
    """Runs yeelightble as a daemon"""
    logger.info(f'Starting yeelightble service daemon v{__version__}')
    server = Server()
    asyncio.run(server.start(host=host, port=port))


@cli.command()
@click.option("-t", "--timeout", default=5, required=False)
def scan(timeout):
    """Scan for bluetooth devices"""
    scanner = BTLEScanner(timeout=timeout)
    scanner.scan()


@cli.command()
@pass_dev
def state(dev: Lamp):
    """ Requests the state from the device. """
    dev.get_state()
    wait_for_result_and_exit()


@pass_dev
def wait_for_result_and_exit(dev: Lamp):
    dev.wait_for_notifications()
    click.echo("MAC: %s" % dev.mac)
    click.echo("State: %s" % dev.state)
    sys.exit()


@cli.command()
@pass_dev
def on(dev: Lamp):
    """ Turns the lamp on. """
    dev.turn_on()


@cli.command()
@pass_dev
def off(dev: Lamp):
    """ Turns the lamp off. """
    dev.turn_off()


@cli.command()
@click.argument("brightness", type=int, default=None, required=False)
@pass_dev
def brightness(dev: Lamp, brightness):
    """ Gets or sets the brightness. """
    if brightness:
        click.echo("Setting brightness to %s" % brightness)
        dev.set_brightness(brightness)
    else:
        click.echo("Brightness: %s" % dev.brightness)


@cli.command()
@click.argument("red", type=int, default=None, required=False)
@click.argument("green", type=int, default=None, required=False)
@click.argument("blue", type=int, default=None, required=False)
@click.argument("brightness", type=int, default=None, required=False)
@pass_dev
def color(dev: Lamp, red, green, blue, brightness):
    """ Gets or sets the color. """
    if red or green or blue:
        click.echo("Setting color: %s %s %s (brightness: %s)" % (red, green, blue, brightness))
        dev.set_color(red, green, blue, brightness)
    else:
        click.echo("Color: %s" % (dev.color,))


@cli.command()
@click.argument('temperature', type=int, default=None, required=False)
@click.argument('brightness', type=int, default=None, required=False)
@pass_dev
def temperature(dev: Lamp, temperature, brightness):
    """ Gets and sets the color temperature 1700-6500K """
    if temperature:
        click.echo("Setting the temperature to %s (brightness: %s)" % (temperature, brightness))
        dev.set_temperature(temperature, brightness)
    else:
        click.echo("Temperature: %s" % dev.temperature)


@cli.command()
@pass_dev
def name(dev: Lamp):
    dev.get_name()
    wait_for_result_and_exit()


@cli.command(name="info")
@pass_dev
def device_info(dev: Lamp):
    """Returns hw & sw version."""
    dev.get_version_info()
    dev.get_serial_number()
    wait_for_result_and_exit()


@cli.command(name="time")
@click.argument("new_time", default=None, required=False)
@pass_dev
def time_(dev: Lamp, new_time):
    """Gets or sets the time."""
    if new_time:
        click.echo("Setting the time to %s" % new_time)
        dev.set_time(new_time)
    else:
        click.echo("Requesting time.")
        dev.get_time()


@cli.command()
@click.argument("number", type=int, default=255, required=False)
@click.argument("name", type=str, required=False)
@pass_dev
def scene(dev: Lamp, number, name):
    if name:
        dev.set_scene(number, name)
    else:
        dev.get_scene(number)


@cli.command()
@click.argument("number", type=int, default=255, required=False)
@pass_dev
def alarm(dev: Lamp, number):
    """Gets alarms."""
    dev.get_alarm(number)


@cli.command()
@pass_dev
def night_mode(dev: Lamp):
    """Gets or sets night mode settings."""
    dev.get_nightmode()


@cli.command()
@click.argument("number", type=int, default=255, required=False)
@pass_dev
def flow(dev: Lamp, number):
    dev.get_flow(number)


@cli.command()
@click.argument("time", type=int, default=0, required=False)
@pass_dev
def sleep(dev: Lamp):
    dev.get_sleep()


@cli.command()
@pass_dev
def mode(dev: Lamp):
    click.echo("Mode: %s" % dev.mode)


if __name__ == "__main__":
    cli()
