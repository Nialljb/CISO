#!/usr/bin/env python
"""The run script."""
import json
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import List, Tuple, Union

from flywheel_gear_toolkit import GearToolkitContext
#from flywheel_gear_toolkit.utils.file import sanitize_filename
#from flywheel_gear_toolkit.utils.metadata import Metadata
#from flywheel_gear_toolkit.utils.zip_tools import zip_output

# import flywheel functions
#from fw_gear_ants_ciso.main import prepare, run
from fw_gear_ants_ciso.parser import parse_config
from fw_gear_ants_ciso.generate_command import generate_command
from fw_gear_ants_ciso.command_line import exec_command

#from utils.dry_run import pretend_it_ran

# The gear is split up into 2 main components. The run.py file which is executed
# when the container runs. The run.py file then imports the rest of the gear as a
# module.

log = logging.getLogger(__name__)

def main(context: GearToolkitContext) -> None:
    """Parses config and runs."""
    # TO DO: parse configeration
    gear_inputs, gear_options, app_options = parse_config(context)

    #print("gear options are",  gear_options)
    #print("app options are",  app_options)

    command = generate_command(gear_inputs, gear_options, app_options)
    print(command)

    #This is what it is all about
    exec_command(
    command,
    dry_run=gear_options["dry-run"],
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