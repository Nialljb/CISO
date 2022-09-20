""" This "dry run" integration test doesn't download any data, but copies it from the
provided zip file and then pretends it runs the BIDS-App command.
"""

import json
import logging
from glob import glob
from os import chdir
from pathlib import Path
from unittest.mock import patch

import pytest

import run

FWV0 = Path.cwd()

log = logging.getLogger(__name__)


def test_dry_run_works(
    tmpdir,
    caplog,
    install_gear_results,
    search_caplog_contains,
    check_for_fw_key,
):
    """Test a dry run"""

    caplog.set_level(logging.DEBUG)

    # check for API key; if not found, it skips this test:
    check_for_fw_key(Path.home() / ".config/flywheel/user.json")

    zip_filename = Path("dry_run.zip")
    install_gear_results(zip_filename, tmpdir)
    # the "install_gear_results" unzips the contents of 'zip_filename' into a folder of
    # the same name:
    chdir(tmpdir / zip_filename.stem)

    with run.GearToolkitContext(input_args=[]) as gtk_context:

        # add the "custom" and "name" fields to the context (get it from the
        # manifest.json), in case the job specified in the config.json in the zip file
        # doesn't have those fields:
        with open(FWV0 / "manifest.json", "r", encoding="utf8") as f:
            manifest = json.load(f)
        for key in ["custom", "name"]:
            if key not in gtk_context.manifest:
                gtk_context.manifest[key] = manifest[key]

        # call run.main, patching install_freesurfer_license:
        with pytest.raises(SystemExit) as pytest_exit, patch(
            "run.install_freesurfer_license"
        ):
            run.main(gtk_context)

    assert pytest_exit.value.code == 0
    assert (tmpdir / zip_filename.stem / "work" / "bids" / ".bidsignore").exists()
    assert search_caplog_contains(caplog, "Not running BIDS validation")
    assert search_caplog_contains(caplog, "Executing command", "participant")
    assert search_caplog_contains(caplog, "Executing command", "arg1 arg2")
    assert search_caplog_contains(caplog, "Zipping work directory")
    assert search_caplog_contains(caplog, "Zipping work/bids/dataset_description.json")
    assert search_caplog_contains(caplog, "Zipping work/bids/sub-")
    assert glob(
        str(
            tmpdir
            / zip_filename.stem
            / "output"
            / f"bids-qsiprep_*{gtk_context.destination['id']}.zip"
        )
    )
    assert search_caplog_contains(caplog, "Warning: gear-dry-run is set")
    # assert (tmpdir / zip_filename.stem / "output" / ".metadata.json").exists()
