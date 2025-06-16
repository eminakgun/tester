import click
import logging
import yaml
from pathlib import Path
from typing import Optional

DEFAULT_CONFIG_FILES = ["tester.yml", "config.yml"]

from config.config_manager import ConfigManager
from build_systems.makefile import MakefileBuildSystem
from build_systems.edalize_integration import EdalizeIntegration

logger = logging.getLogger(__name__)


def find_config_file(config_file: Optional[str] = None) -> str:
    """Find the configuration file to use.

    Args:
        config_file: Optional path to config file specified by user

    Returns:
        str: Path to the config file to use

    Raises:
        click.FileError: If no valid config file is found
    """
    # If config file is specified, use it
    if config_file:
        config_path = Path(config_file).absolute()
        if not config_path.is_file():
            raise click.FileError(config_file, "Configuration file not found")
        return str(config_path)

    # Look for default config files
    for default_file in DEFAULT_CONFIG_FILES:
        config_path = Path(default_file).absolute()
        if config_path.is_file():
            logger.debug(f"Using config file: {default_file}")
            return str(config_path)

    # No config file found
    raise click.FileError(
        "tester.yml/config.yml", "No configuration file found. Create tester.yml or config.yml, or specify with --config"
    )


def load_config(config_file: Optional[str] = None) -> dict:
    """Load configuration from file."""
    config_path = find_config_file(config_file)

    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise click.FileError(config_path, f"Invalid YAML format: {e}")
    except Exception as e:
        raise click.FileError(config_path, f"Failed to load config: {e}")


def get_build_system(config: dict):
    """Create build system based on configuration."""
    build_system_type = config.get("build_system", "makefile")

    if build_system_type == "makefile":
        return MakefileBuildSystem(config)
    elif build_system_type == "edalize":
        return EdalizeIntegration(config)
    else:
        raise ValueError(f"Unsupported build system: {build_system_type}")


def get_default_testbench(config: dict) -> str:
    """Get the default testbench from config or first available testbench."""
    # First try to get explicitly configured default
    default_tb = config.get("default_testbench")
    if default_tb:
        return default_tb

    # If no default is set, try to get the first testbench from config
    testbenches = config.get("template_config", {}).get("testbenches", {})
    if testbenches:
        return next(iter(testbenches))

    raise click.UsageError("No default testbench configured and no testbenches found in config")


@click.group()
@click.option("--config", "-c", help="Configuration file path")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(ctx, config: str, verbose: bool):
    """UVM Testbench Automation Tool"""
    # Set up logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=log_level)

    # Load configuration
    try:
        ctx.obj = load_config(config)
    except click.FileError as e:
        logger.error(str(e))
        ctx.exit(1)


@cli.command()
@click.pass_obj
def list_testbenches(config):
    """List available testbenches"""
    try:
        build_system = get_build_system(config)
        testbenches = build_system.get_available_testbenches()

        if not testbenches:
            click.echo("No testbenches found")
            return

        click.echo("Available testbenches:")
        for tb in testbenches:
            click.echo(f"  - {tb}")
    except Exception as e:
        logger.error(f"Failed to list testbenches: {e}")
        raise click.Abort()


@cli.command()
@click.argument("testbench", required=False)
@click.pass_obj
def list_tests(config, testbench: str):
    """List available tests for a testbench"""
    try:
        if not testbench:
            testbench = get_default_testbench(config)

        build_system = get_build_system(config)
        tests = build_system.get_available_tests(testbench)

        if not tests:
            click.echo(f"No tests found for testbench '{testbench}'")
            return

        click.echo(f"Available tests for {testbench}:")
        for test in tests:
            click.echo(f"  - {test}")
    except Exception as e:
        logger.error(f"Failed to list tests: {e}")
        raise click.Abort()


@cli.command()
@click.argument("testbench", required=False)
@click.option("--debug", is_flag=True, help="Enable debug build")
@click.option("--incremental", is_flag=True, help="Enable incremental build")
@click.pass_obj
@click.pass_context
def build(ctx, config, testbench: str, debug: bool, incremental: bool):
    """Build a testbench"""
    try:
        if not testbench:
            testbench = get_default_testbench(config)

        build_system = get_build_system(config)
        options = {
            "debug": debug,
            "incremental": incremental,
            "verbose": ctx.parent.params.get("verbose", False),  # Get verbose flag from parent context
        }

        if build_system.build(testbench, options):
            click.echo(f"Successfully built testbench '{testbench}'")
        else:
            click.echo(f"Failed to build testbench '{testbench}'")
            raise click.Abort()
    except Exception as e:
        logger.error(f"Failed to build testbench: {e}")
        raise click.Abort()


@cli.command()
@click.argument("arg1", required=False)
@click.argument("arg2", required=False)
@click.option("--testbench", "-t", help="Testbench name (alternative to positional argument)")
@click.option("--seed", type=int, help="Random seed for test")
@click.option("--verbosity", type=click.Choice(["LOW", "MEDIUM", "HIGH", "DEBUG"], case_sensitive=False))
@click.option("--coverage", is_flag=True, help="Enable coverage collection")
@click.option("--runtime-args", "-r", multiple=True, help="Additional runtime arguments (can be used multiple times)")
@click.pass_obj
@click.pass_context
def run(
    ctx,
    config,
    arg1: Optional[str],
    arg2: Optional[str],
    testbench: Optional[str],
    seed: Optional[int],
    verbosity: Optional[str],
    coverage: bool,
    runtime_args: tuple,
):
    """Run a specific test

    Usage:
      tester run [TESTBENCH] TEST
      tester run TEST --testbench TESTBENCH
      tester run TEST  (uses default testbench)
    """
    try:
        # Add debug logging
        logger.debug(f"Config type: {type(config)}")
        logger.debug(f"Config content: {config}")

        # Determine testbench and test from arguments
        if arg1 and arg2:
            # Two positional args: first is testbench, second is test
            tb_name = arg1
            test_name = arg2
        elif arg1 and testbench:
            # One positional arg + --testbench option: arg1 is test, testbench is from option
            tb_name = testbench
            test_name = arg1
        elif arg1:
            # Only one positional arg: it's the test name, use default testbench
            test_name = arg1
            tb_name = testbench or get_default_testbench(config)
        else:
            # No positional args: error
            raise click.UsageError("Test name is required")

        build_system = get_build_system(config)
        options = {
            "coverage": coverage,
            "verbose": ctx.parent.params.get("verbose", False),  # Get verbose flag from parent context
        }

        if seed is not None:
            options["seed"] = seed

        if verbosity:
            options["verbosity"] = verbosity

        # Get test-specific runtime args from config
        test_config = config.get("testbenches", {}).get(tb_name, {}).get("tests", {}).get(test_name, {})
        config_runtime_args = test_config.get("runtime_args", [])

        # Combine config runtime args with command-line runtime args
        # Make sure config_runtime_args is a list
        if isinstance(config_runtime_args, list):
            all_runtime_args = list(config_runtime_args)
        else:
            # Handle the case where it might be something else
            all_runtime_args = []
            if config_runtime_args:
                all_runtime_args.append(str(config_runtime_args))

        all_runtime_args.extend(runtime_args)

        if all_runtime_args:
            options["runtime_args"] = all_runtime_args

        if build_system.run(tb_name, test_name, options):
            click.echo(f"Successfully ran test '{test_name}' for testbench '{tb_name}'")
        else:
            click.echo(f"Failed to run test '{test_name}' for testbench '{tb_name}'")
            raise click.Abort()
    except Exception as e:
        logger.error(f"Failed to run test: {e}")
        raise click.Abort()


@cli.command()
@click.argument("testbench", required=False)
@click.pass_obj
def clean(config, testbench: str):
    """Clean testbench artifacts"""
    try:
        build_system = get_build_system(config)
        if build_system.clean(testbench):
            click.echo(f"Successfully cleaned testbench '{testbench}'")
        else:
            click.echo(f"Failed to clean testbench '{testbench}'")
            raise click.Abort()
    except Exception as e:
        logger.error(f"Failed to clean testbench: {e}")
        raise click.Abort()


if __name__ == "__main__":
    cli(obj=None)  # Pass None as the initial obj value
