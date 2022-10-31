"""Parser module to parse gear config.json."""
from typing import Tuple

from flywheel_gear_toolkit import GearToolkitContext

from utils.fly.set_performance_config import set_mem_gb, set_n_cpus


def parse_config(
    gear_context: GearToolkitContext,
) -> Tuple[dict, dict]:
    """Parse the config and other options from the context, both gear and app options.

    Returns:
        gear_options: options for the gear
        app_options: options to pass to the app
    """
    # ##   Gear config   ## #

    gear_options = {
        "bids-app-binary": gear_context.manifest.get("custom").get("bids-app-binary"),
        # These are the BIDS modalities that will be downloaded from the instance
        "bids-app-modalities": gear_context.manifest.get("custom").get(
            "bids-app-modalities"
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

    # pylint: disable=pointless-string-statement
    """ Notes on inputs:  These notes follow the input order as documented here:
     https://qsiprep.readthedocs.io/en/latest/usage.html#command-line-arguments

    * Positional arguments are covered by the template
    * version: SKIPPED, can be passed in as a gear argument
    * skip-bids-validation: SKIPPED combined with the template's "run_validation"
    * participant-label: SKIPPED extracted from parent container
    * bids-database-dir:
    * bids-filter-file:
    * nthreads: SKIPPED, handled by template
    * omp-nthreads: SKIPPED, handled by template
    * mem_mb: SKIPPED, handled by template
    * low-mem: SKIPPED, not necessary
    * reports-only: ADDED for ease of access
    All other options from the "Other Options" section are left out, as these can be
    passed into the "bids_app_args" section
    """
    # pylint: enable=pointless-string-statement

    app_options_keys = [
        "bids_app_args",
        "interactive-reports-only",
        "acquisition_type",
        "infant",
        "boilerplate",
        "verbose",
        "longitudinal",
        "reports-only",
        "n_cpus",
        "mem_mb",
        "write-graph",
        "ignore",
        "image_dimension",
        "iterations_limit",
        "max_iterations",
        "modality_dimension",
        "shrink_factor",
        "smoothing_factor",
        "similarity_metric",
        "transformation_type",
        "transformation_model",
        "output_prefix",
        "target_template",
        "Rigid-body_registration",
        "Input Glob Pattern",
        "Input Regex",
        "Input Tags"
    ]
    
    app_options = {key: gear_context.config.get(key) for key in app_options_keys}

    app_options["n_cpus"] = set_n_cpus(app_options["n_cpus"])
    # set integer:
    app_options["mem_mb"] = int(1024 * set_mem_gb((app_options["mem_mb"] or 0) / 1024))

    return gear_options, app_options
