"""Parser module to parse gear config.json."""

from typing import Tuple
from app.context import GearToolkitContext

def parse_config(
    gear_context: GearToolkitContext,
) -> Tuple[dict, dict, dict]: # Add dict for each set of outputs
    """Parse the config and other options from the context, both gear and app options.

    Returns:
        gear_inputs
        gear_options: options for the gear
        app_options: options to pass to the app
    """

    # Gear Inputs
    gear_inputs = {
        "input1" : gear_context.get_input("input1"), # label in manifest
        "input2" : gear_context.get_input("input2"),
        "input3" : gear_context.get_input("input3")
    }

    # ##   Gear config   ## #
    # some options here not relevent/called
    gear_options = {
        "kcl-app-binary": gear_context.manifest.get("custom").get("kcl-app-binary"),
        "kcl-app-modalities": gear_context.manifest.get("custom").get(
            "kcl-app-modalities"
        ),
        "analysis-level": gear_context.manifest.get("custom").get("analysis-level"),
        "ignore-bids-errors": gear_context.config.get("gear-ignore-bids-errors"),
        "run-bids-validation": gear_context.config.get("gear-run-bids-validation"),
        "save-intermediate-output": gear_context.config.get(
            "gear-save-intermediate-output"
        ),
        "intermediate-files": gear_context.config.get("gear-intermediate-files"),
        "intermediate-folders": gear_context.config.get("gear-intermediate-folders"),
        "dry-run": gear_context.config.get("gear-dry-run"),
        "keep-output": gear_context.config.get("gear-keep-output"),
        "output-dir": gear_context.output_dir,
        "destination-id": gear_context.destination["id"],
        "work-dir": gear_context.work_dir,
        "client": gear_context.client,
    }

    # set the output dir name for the BIDS app:
    gear_options["output_analysis_id_dir"] = (
        gear_options["output-dir"] / gear_options["destination-id"]
    )

    # ##   App options:   ## #
    """ Notes on inputs:  These notes follow the input order as documented here:
    https://github.com/ANTsX/ANTs/blob/master/Scripts/antsMultivariateTemplateConstruction2.sh 

    All other options from the "Other Options" section are left out, as these can be
    passed into the "bids_app_args" section
    """

    # TO DO: update keys here & in manifest
    app_options_keys = [
    #"bids_app_args",
    "imageDimension", # d
    "Iteration", # i
    "maxIterations", # r
    "modalityNum", # k
    "shrinkFactor", # f
    "smoothingFactor", # s
    "similarityMetric", # q
    "transformationType", # t
    "transformationModel", # m
    "prefix" # o
]
    
    app_options = {key: gear_context.config.get(key) for key in app_options_keys}

    return gear_inputs, gear_options, app_options