#!/usr/bin/env python
"""The run script."""
import logging
import os
from pathlib import Path
from typing import List, Tuple, Union

# import flywheel functions
from flywheel_gear_toolkit import GearToolkitContext
from app.parser import parse_config
from app.generate_command import generate_command
from app.command_line import exec_command
# The gear is split up into 2 main components. The run.py file which is executed
# when the container runs. The run.py file then imports the rest of the gear as a
# module.

log = logging.getLogger(__name__)

def main(context: GearToolkitContext) -> None:
    """Parses config and runs."""
    gear_inputs, gear_options, app_options = parse_config(context)

    # 1. Simple smooth brain version
    command = "/flywheel/v0/app/ciso-gear.sh"
    #os.system(command)

    # 2. FW control submission run/error logs
    #command = generate_command(gear_inputs, gear_options, app_options)
    print(command)
    #This is what it is all about
    exec_command(
    command,
    #dry_run=gear_options["dry-run"],
    shell=True,
    cont_output=True,
        )

# Only execute if file is run as main, not when imported by another module
if __name__ == "__main__":  # pragma: no cover
    # Get access to gear config, inputs, and sdk client if enabled.
    with GearToolkitContext() as gear_context:

        # Initialize logging, set logging level based on `debug` configuration
        # key in gear config.
        gear_context.init_logging()

        # Pass the gear context into main function defined above.
        main(gear_context)