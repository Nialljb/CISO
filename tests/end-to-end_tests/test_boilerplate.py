""" This integration test downloads a sample dataset from ga.ce.flywheel.io and then
runs the BIDS-App with the "--boilerplate" option.

This just generates the boilerplate information, but it doesn't run anything else.
However, it allows us to test the app dependencies.
"""


import json
import logging
import os
from glob import glob
from pathlib import Path

import pytest

import run

FWV0 = Path.cwd()

log = logging.getLogger(__name__)


@pytest.mark.skipif(
    not Path("/flywheel/v0/").is_dir()
    or not os.access(
        Path(os.environ.get("FREESURFER_HOME", run.FREESURFER_HOME)) / "license.txt",
        os.W_OK,
    ),
    reason="Only for testing inside container",
)
def test_boilerplate_run(
    tmpdir,
    caplog,
    install_gear_results,
    search_caplog_contains,
    check_for_fw_key,
):
    """Test a real run of the BIDS-App

    Use the --boilerplate option so that the bids-app binary gets called
    """

    caplog.set_level(logging.DEBUG)

    # check for API key; if not found, it skips this test:
    check_for_fw_key(Path.home() / ".config/flywheel/user.json")

    zip_filename = Path("boilerplate_run.zip")
    install_gear_results(zip_filename, tmpdir)
    # the "install_gear_results" unzips the contents of 'zip_filename' into a folder of
    # the same name:
    os.chdir(tmpdir / zip_filename.stem)

    with run.GearToolkitContext(input_args=[]) as gtk_context:

        # add the "custom" and "name" fields to the context (get it from the
        # manifest.json), in case the job specified in the config.json in the zip file
        # doesn't have those fields:
        with open(FWV0 / "manifest.json", "r", encoding="utf8") as f:
            manifest = json.load(f)
        for key in ["custom", "name"]:
            if key not in gtk_context.manifest:
                gtk_context.manifest[key] = manifest[key]

        with pytest.raises(SystemExit) as pytest_exit:
            run.main(gtk_context)

    assert pytest_exit.value.code == 0
    assert (tmpdir / zip_filename.stem / "work" / "bids" / ".bidsignore").exists()
    assert search_caplog_contains(caplog, "No BIDS errors detected.")
    assert search_caplog_contains(caplog, "Downloading BIDS data was successful")
    assert search_caplog_contains(caplog, "command is", "participant")
    assert search_caplog_contains(caplog, "command is", "--boilerplate")
    assert glob(
        str(
            tmpdir
            / zip_filename.stem
            / "output"
            / f"bids-qsiprep_*{gtk_context.destination['id']}.zip"
        )
    )
    # assert (tmpdir / zip_filename.stem / "output" / ".metadata.json").exists()
