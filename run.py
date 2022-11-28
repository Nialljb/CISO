#!/usr/bin/env python
"""The run script."""
import json
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import List, Tuple, Union

# import flywheel functions
from flywheel_gear_toolkit import GearToolkitContext
#from app.main import prepare, run
from app.parser import parse_config
from app.generate_command import generate_command
from app.command_line import exec_command
from app.beta_triplane_SRImageReconViaANTS import beta_triplane_SRImageReconViaANTS

# The gear is split up into 2 main components. The run.py file which is executed
# when the container runs. The run.py file then imports the rest of the gear as a
# module.

log = logging.getLogger(__name__)

def main(context: GearToolkitContext) -> None:
    """Parses config and runs."""
    gear_inputs, gear_options, app_options = parse_config(context)

    #print("gear options are",  gear_options)
    #print("app options are",  app_options)

    # 1. From Seans paper (missing script)
    #command = beta_triplane_SRImageReconViaANTS(gear_inputs, gear_options, app_options)
    #beta_triplane_SRImageReconViaANTS(gear_inputs, gear_options, app_options)
    # 2. Flywheel structure (execute command syntax issue)
    #command = generate_command(gear_inputs, gear_options, app_options)
    # 3. Simple smooth brain version
    
    command = "/flywheel/v0/app/beta-gear.sh"
    os.system(command)

    # #This is what it is all about
    # exec_command(
    # command,
    # #dry_run=gear_options["dry-run"],
    # shell=True,
    # cont_output=True,
    #     )

# Only execute if file is run as main, not when imported by another module
if __name__ == "__main__":  # pragma: no cover
    # Get access to gear config, inputs, and sdk client if enabled.
    with GearToolkitContext() as gear_context:

        # Initialize logging, set logging level based on `debug` configuration
        # key in gear config.
        gear_context.init_logging()

        # Pass the gear context into main function defined above.
        main(gear_context)