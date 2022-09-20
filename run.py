#!/usr/bin/env python
"""The run script."""
import json
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import List, Tuple, Union

from flywheel_bids.results.zip_htmls import zip_htmls
from flywheel_bids.results.zip_intermediate import (
    zip_all_intermediate_output,
    zip_intermediate_selected,
)
from flywheel_bids.utils.download_run_level import download_bids_for_runlevel
from flywheel_bids.utils.run_level import get_analysis_run_level_and_hierarchy
from flywheel_gear_toolkit import GearToolkitContext
from flywheel_gear_toolkit.licenses.freesurfer import install_freesurfer_license
from flywheel_gear_toolkit.utils.file import sanitize_filename
from flywheel_gear_toolkit.utils.metadata import Metadata
from flywheel_gear_toolkit.utils.zip_tools import zip_output

# This design with the main interfaces separated from a gear module (with main and
# parser) allows the gear module to be publishable, so it can then be imported in
# another project, which enables chaining multiple gears together.
from fw_gear_bids_qsiprep.main import prepare, run
from fw_gear_bids_qsiprep.parser import parse_config
from utils.dry_run import pretend_it_ran

# The gear is split up into 2 main components. The run.py file which is executed
# when the container runs. The run.py file then imports the rest of the gear as a
# module.

log = logging.getLogger(__name__)

# Default/fall-back folder for the FS license (in case ${FREESURFER_HOME} is not defined
# in the environment:
FREESURFER_HOME = "/opt/freesurfer"


def get_bids_data(
    context: GearToolkitContext,
    gear_options: dict,
    tree_title: str,
) -> Tuple[str, str, List[str]]:
    """Get the data in BIDS structure.

    Get the data in BIDS structure and return the subject_label and
    run_label corresponding to the destination container.
    It also returns any error found downloading the BIDS data.

    For FW gears, it downloads the data
    For RL containers, it just points/links to the storage folder
    It should be independent of the specific BIDS-App

    Args:
        context (GearToolkitContext): gear context
        gear_options (Dict): gear options
        tree_title (str): title for the BIDS tree

    Returns:
        subject_label (str): FW subject_label, (from the hierarchy of the destination
            container)
        run_label (str): FW run_label, (from the hierarchy of the destination container)
        errors (list[str]): list of generated errors
    """
    errors = []

    # Given the destination container, figure out if running at the project,
    # subject, or session level.
    hierarchy = get_analysis_run_level_and_hierarchy(
        context.client, context.destination["id"]
    )

    # This is the label of the project, subject or session and is used
    # as part of the name of the output files.
    run_label = hierarchy["run_label"]
    run_label = sanitize_filename(run_label)

    # Create HTML file that shows BIDS "Tree" like output
    tree = True

    error_code = download_bids_for_runlevel(
        context,
        hierarchy,
        tree=tree,
        tree_title=tree_title,
        src_data=False,
        folders=gear_options["bids-app-modalities"],
        dry_run=gear_options["dry-run"],
        do_validate_bids=gear_options["run-bids-validation"],
    )
    if error_code > 0 and not gear_options["ignore-bids-errors"]:
        errors.append("BIDS Error(s) detected")

    return hierarchy["subject_label"], run_label, errors


# pylint: disable=too-many-arguments
def post_run(
    gear_name: str,
    gear_options: dict,
    analysis_output_dir: Union[str, Path],
    run_label: str,
    errors: List[str],
    warnings: List[str],
) -> None:
    """Move all the results to the final destination, clean-up.

    Args:
        gear_name (str): gear name, used in the output file names
        gear_options (dict): gear options
        analysis_output_dir (str or Path): name of the output dir
        run_label (str): run label (project|subject|session label)
        errors (list[str]): list of errors found
        warnings (list[str]): list of warnings found
    """
    # zip entire output/<analysis_id> folder into
    #  <gear_name>_<project|subject|session label>_<analysis.id>.zip
    zip_file_name = f"{gear_name}_{run_label}_{gear_options['destination-id']}.zip"
    zip_output(
        str(gear_options["output-dir"]),
        gear_options["destination-id"],
        zip_file_name,
        dry_run=False,
        exclude_files=None,
    )

    # zip any .html files in output/<analysis_id>/
    html_dir = Path(analysis_output_dir) / "qsiprep"
    zip_htmls(str(analysis_output_dir), gear_options["destination-id"], html_dir)

    # possibly save ALL intermediate output
    if gear_options["save-intermediate-output"]:
        zip_all_intermediate_output(
            gear_options["destination-id"],
            gear_name,
            gear_options["output-dir"],
            gear_options["work-dir"],
            run_label,
        )

    # possibly save intermediate files and folders
    zip_intermediate_selected(
        gear_options["intermediate-files"],
        gear_options["intermediate-folders"],
        gear_options["destination-id"],
        gear_name,
        gear_options["output-dir"],
        gear_options["work-dir"],
        run_label,
    )

    # clean up: remove output that was zipped
    if Path(analysis_output_dir).exists():
        if not gear_options["keep-output"]:

            log.debug('removing output directory "%s"', str(analysis_output_dir))
            shutil.rmtree(analysis_output_dir)

        else:
            log.info('NOT removing output directory "%s"', str(analysis_output_dir))

    else:
        log.info("Output directory does not exist so it cannot be removed")

    # Report errors and warnings at the end of the log, so they can be easily seen.
    if len(warnings) > 0:
        msg = "Previous warnings:\n"
        for warn in warnings:
            msg += "  Warning: " + str(warn) + "\n"
        log.info(msg)

    if len(errors) > 0:
        msg = "Previous errors:\n"
        for err in errors:
            if str(type(err)).split("'")[1] == "str":
                # show string
                msg += "  Error msg: " + str(err) + "\n"
            else:  # show type (of error) and error message
                err_type = str(type(err)).split("'")[1]
                msg += f"  {err_type}: {str(err)}\n"
        log.info(msg)


# pylint: enable=too-many-arguments


def save_metadata(
    context: GearToolkitContext, work_dir: Path, extra_info: dict = None
) -> None:
    """Write out any metadata.

    Args:
        context (GearToolkitContext): gear context
        work_dir (Path): path to the work dir
        extra_info (dict): extra info to add to the metadata (optional)
    """
    dwiqc_info = {}
    # Get the dwiqc.json info generated by the gear:
    dwiqc_json = work_dir / "dwiqc.json"
    if dwiqc_json.exists():
        with open(dwiqc_json, "r", encoding="utf8") as json_file:
            dwiqc_info = json.load(json_file)

    if extra_info:
        dwiqc_info.update(extra_info)

    # Write the metadata (in the "results" namespace) using the gear_toolkit
    # Metadata class:
    my_metadata = Metadata(context)
    my_metadata.add_gear_info("results", context.destination["id"], **dwiqc_info)


# pylint: disable=too-many-locals,too-many-statements
def main(context: GearToolkitContext) -> None:
    """Parses config and runs."""
    # For now, don't allow runs at the project level:
    destination = context.client.get(context.destination["id"])
    if destination.parent.type == "project":
        log.exception(
            "This version of the gear does not run at the project level. "
            "Try running it for each individual subject."
        )
        sys.exit(1)

    # Errors and warnings will always be logged when they are detected.
    # Keep a list of errors and warning to print all in one place at end of log
    # Any errors will prevent the BIDS App from running.
    errors = []
    warnings = []

    # Call the fw_gear_bids_qsiprep.parser.parse_config function
    # to extract the args, kwargs from the context (e.g. config.json).
    gear_options, app_options = parse_config(context)

    # TO-DO: install_freesurfer_license from the gear_toolkit takes the gear context as
    #    an argument, so it is only valid for FW instances. However, the functionality
    #    of taking a FreeSurfer license (either string or file) and copying it to
    #    wherever your app expects it should be the same whether you run it on FW, or
    #    XNAT or HPC or locally.
    #    In the future, it would be great to have a "instance-independent"
    #    install_freesurfer_license and have a "instance-dependent" function to extract
    #    the license from the context. At that point, we could extract the license e.g.
    #    in the parser, and this function can be moved to fw_gear_bids_qsiprep.main
    install_freesurfer_license(
        context,
        Path(os.environ.get("FREESURFER_HOME", FREESURFER_HOME)) / "license.txt",
    )

    prepare_errors, prepare_warnings = prepare(
        gear_options=gear_options,
        app_options=app_options,
    )
    errors += prepare_errors
    warnings += prepare_warnings

    if len(errors) == 0:
        tree_title = f"{sanitize_filename(gear_options['bids-app-binary'])} BIDS Tree"
        subject_label, run_label, get_bids_errors = get_bids_data(
            context=context,
            gear_options=gear_options,
            tree_title=tree_title,
        )
        errors += get_bids_errors

        # For BIDS-Apps that run at the participant level, set the
        # "participant_label" from the container from which it was launched.
        if gear_options["analysis-level"] == "participant" and not app_options.get(
            "participant_label", ""
        ):
            app_options["participant_label"] = subject_label

        # In general, BIDS-Apps take only the (subject) label, without the "sub-" part:
        if app_options["participant_label"].startswith("sub-"):
            # Write this in two instructions because if you write it in one, Black will
            # format it horribly:
            new_participant_label = app_options["participant_label"][len("sub-") :]
            app_options["participant_label"] = new_participant_label

    else:
        run_label = "error"
        log.info("Did not download BIDS because of previous errors")
        print(errors)

    if len(errors) > 0:
        e_code = 1
        log.info("Command was NOT run because of previous errors.")

    elif gear_options["dry-run"]:
        e_code = 0
        pretend_it_ran(gear_options, app_options)
        save_metadata(
            context,
            gear_options["output_analysis_id_dir"] / "qsiprep",
            {"dry-run": "true"},
        )
        e = "gear-dry-run is set: Command was NOT run."
        log.warning(e)
        warnings.append(e)

    else:
        try:
            # Pass the args, kwargs to fw_gear_qsiprep.main.run function to execute
            # the main functionality of the gear.
            e_code = run(gear_options, app_options)

        except RuntimeError as exc:
            e_code = 1
            errors.append(str(exc))
            log.critical(exc)
            log.exception("Unable to execute command.")

        else:
            # We want to save the metadata only if the run was successful.
            # We want to save partial outputs in the event of the app crashing, because
            # the partial outputs can help pinpoint what the exact problem was. So we
            # have `post_run` further down.
            save_metadata(context, gear_options["output_analysis_id_dir"] / "qsiprep")

    # Cleanup, move all results to the output directory.
    # post_run should be run regardless of dry-run or exit code.
    # It will be run even in the event of an error, so that the partial results are
    # available for debugging.
    post_run(
        gear_name=context.manifest["name"],
        gear_options=gear_options,
        analysis_output_dir=str(gear_options["output_analysis_id_dir"]),
        run_label=run_label,
        errors=errors,
        warnings=warnings,
    )

    gear_builder = context.manifest.get("custom").get("gear-builder")
    # gear_builder.get("image") should be something like:
    # flywheel/bids-qsiprep:0.0.1_0.15.1
    container = gear_builder.get("image").split(":")[0]
    log.info("%s Gear is done.  Returning %s", container, e_code)

    # Exit the python script (and thus the container) with the exit
    # code returned by fw_gear_bids_qsiprep.main.run function.
    sys.exit(e_code)


# pylint: enable=too-many-locals,too-many-statements


# Only execute if file is run as main, not when imported by another module
if __name__ == "__main__":  # pragma: no cover
    # Get access to gear config, inputs, and sdk client if enabled.
    with GearToolkitContext() as gear_context:

        # Initialize logging, set logging level based on `debug` configuration
        # key in gear config.
        gear_context.init_logging()

        # Pass the gear context into main function defined above.
        main(gear_context)
