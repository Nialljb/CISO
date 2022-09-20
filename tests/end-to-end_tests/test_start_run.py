""" This integration test downloads a sample dataset from ga.ce.flywheel.io and then
starts a run of the BIDS-App

Because even if we used the "--sloppy" option and low resolution data, a full run takes
about 10 hrs., we execute the call with "timeout" and a customizable time (set in the
"allowed_run_time_min" global)
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

allowed_run_time_min = 3


@pytest.mark.skipif(
    not Path("/flywheel/v0/").is_dir()
    or not os.access(
        Path(os.environ.get("FREESURFER_HOME", run.FREESURFER_HOME)) / "license.txt",
        os.W_OK,
    ),
    reason="Only for testing inside container",
)
def test_start_run(
    tmpdir,
    caplog,
    install_gear_results,
    search_caplog_contains,
    check_for_fw_key,
):
    """Test a real run of the BIDS-App

    Shorten the run by using the "timeout" shell command (allowed_run_time_min minutes)
    By allowing it to start the actual run, we make sure that the gear installs the
    FreeSurfer license, downloads real data, runs the validator on them and starts the
    qsiprep processing. Minimum time required for these steps is 3 minutes.
    """
    caplog.set_level(logging.DEBUG)

    # check for API key; if not found, it skips this test:
    check_for_fw_key(Path.home() / ".config/flywheel/user.json")

    zip_filename = Path("start_run.zip")
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
        # Override the "bids-app-binary" so that it times out after a certain time.
        # This allows us to check that the call works and qsiprep starts running.
        bids_app_binary = gtk_context.manifest["custom"].get("bids-app-binary")
        gtk_context.manifest["custom"][
            "bids-app-binary"
        ] = f"timeout {allowed_run_time_min}m {bids_app_binary}"

        with pytest.raises(SystemExit) as pytest_exit:
            run.main(gtk_context)

    # Because it timed-out, the command will not return success, but the log will have
    # the code returned by "timeout" (= 124)
    assert pytest_exit.value.code == 1
    assert search_caplog_contains(caplog, "Command return code: 124")
    assert (tmpdir / zip_filename.stem / "work" / "bids" / ".bidsignore").exists()
    assert search_caplog_contains(caplog, "No BIDS errors detected.")
    assert search_caplog_contains(caplog, "Downloading BIDS data was successful")
    assert search_caplog_contains(caplog, "Executing command", "participant")
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
    # assert (tmpdir / zip_filename.stem / "output" / ".metadata.json").exists()
