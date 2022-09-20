"""Main module."""

import logging
from pathlib import Path
from typing import List, Tuple

from flywheel_gear_toolkit.interfaces.command_line import (
    build_command_list,
    exec_command,
)

log = logging.getLogger(__name__)


def generate_command(
    gear_options: dict,
    app_options: dict,
) -> List[str]:
    """Build the main command line command to run.

    This method should be the same for FW and XNAT instances. It is also BIDS-App
    generic.

    Args:
        gear_options (dict): options for the gear, from config.json
        app_options (dict): options for the app, from config.json
    Returns:
        cmd (list of str): command to execute
    """
    # Common to all BIDS Apps (https://github.com/BIDS-Apps), start with the command
    # itself and the 3 positional args: bids path, output dir, analysis-level
    # ("participant"/"group").
    # This should be done here in case there are nargs='*' arguments
    # (PV: Not sure if this is the case anymore. Their template seems to
    # suggest so, but not the general documentation.)
    cmd = [
        str(gear_options["bids-app-binary"]),
        str(gear_options["work-dir"] / "bids"),
        str(gear_options["output_analysis_id_dir"]),
        str(gear_options["analysis-level"]),
    ]

    # get app parameters and pass them to the command
    command_parameters = {}

    for key, val in app_options.items():

        # these arguments are passed directly to the command as is
        if key == "bids_app_args" and val:
            bids_app_args = val.split(" ")
            # append this list to the cmd:
            cmd.extend(bids_app_args)

        else:
            command_parameters[key] = val

    # check to see if we need to skip the bids-validation:
    if not gear_options["run-bids-validation"]:
        command_parameters["skip-bids-validation"] = True

    cmd = build_command_list(cmd, command_parameters)

    for ii, cc in enumerate(cmd):
        if cc.startswith("--verbose"):
            # The app takes a "-v/--verbose" boolean flag (either present or not),
            # while the config verbose argument would be "--verbose=v".
            # So replace "--verbose=<v|vv|vvv>' with '-<v|vv|vvv>':
            cmd[ii] = "-" + cc.split("=")[1]

        elif " " in cc:
            # When there are spaces in an element of the list, it means that the
            # argument is a space-separated list, so take out the "=" separating the
            # argument from the value. e.g.:
            #     "--foo=bar fam" -> "--foo bar fam"
            # this allows argparse "nargs" to work properly
            cmd[ii] = cc.replace("=", " ")

    log.info("command is: %s", str(cmd))
    return cmd


def prepare(
    gear_options: dict,
    app_options: dict,
) -> Tuple[List[str], List[str]]:
    """Prepare everything for the algorithm run.

    It should:
     - Install FreeSurfer license (if needed)

    Same for FW and RL instances.
    Potentially, this could be BIDS-App independent?

    Args:
        gear_options (Dict): gear options
        app_options (Dict): options for the app

    Returns:
        errors (list[str]): list of generated errors
        warnings (list[str]): list of generated warnings
    """
    # pylint: disable=unused-argument
    # for now, no errors or warnings, but leave this in place to allow future methods
    # to return an error
    errors: List[str] = []
    warnings: List[str] = []

    return errors, warnings
    # pylint: enable=unused-argument


def run(gear_options: dict, app_options: dict) -> int:
    """Run QSIPrep itself.

    Arguments:
        gear_options: dict with gear-specific options
        app_options: dict with options for the BIDS-App

    Returns:
        run_error: any error encountered running the app. (0: no error)
    """
    log.info("This is the beginning of the run file")

    output_analysis_id_dir = Path(gear_options["output-dir"]) / Path(
        gear_options["destination-id"]
    )

    command = generate_command(gear_options, app_options)

    # Create output directory
    log.info("Creating output directory %s", output_analysis_id_dir)
    Path(output_analysis_id_dir).mkdir(parents=True)

    # This is what it is all about
    exec_command(
        command,
        dry_run=gear_options["dry-run"],
        shell=True,
        cont_output=True,
    )

    # if we made it this far, return success:
    run_error = 0

    return run_error
