"""
Set up parameters for testing. Picked up by pytest automatically.
"""

import json
import shutil
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock

import pytest
from flywheel_gear_toolkit import GearToolkitContext
from flywheel_gear_toolkit.utils.zip_tools import unzip_archive


@pytest.fixture
def mocked_gear_options():
    mock_options = {
        "analysis-level": "participant",
        "bids-app-binary": "f00_binary",
        "bids-app-modalities": ["foo", "bar"],
        "dry-run": False,
        "output-dir": "classified",
        "destination-id": "also_classified",
        "run-bids-validation": False,
        "ignore-bids-errors": False,
    }
    mock_options["output_analysis_id_dir"] = (
        Path(mock_options["output-dir"]) / mock_options["destination-id"]
    )
    return mock_options


@pytest.fixture
def mocked_acquisition():
    def _my_mock(parent_type="session"):
        """Return a mocked acquisition with a specific parent.type"""
        my_acquisition = MagicMock()
        my_acquisition.parent.type = parent_type
        return my_acquisition

    return _my_mock


@pytest.fixture
def mocked_context(mocked_gear_options, mocked_acquisition):
    """Return a mocked GearToolkitContext"""
    mocked_manifest = {
        "name": "test",
        "custom": {"gear-builder": {"image": "foo/bar:v1.0"}},
    }
    mocked_destination_id = mocked_gear_options["destination-id"]
    inputs = {}
    return MagicMock(
        spec=GearToolkitContext,
        manifest=mocked_manifest,
        client={mocked_destination_id: mocked_acquisition()},
        destination={"id": mocked_destination_id},
        inputs=inputs,
    )


@pytest.fixture
def mocked_context_for_project_level(mocked_gear_options, mocked_acquisition):
    """Return a mocked GearToolkitContext with a "project" destination parent."""
    mocked_manifest = {
        "name": "test",
        "custom": {"gear-builder": {"image": "foo/bar:v1.0"}},
    }
    mocked_destination_id = mocked_gear_options["destination-id"]
    return MagicMock(
        spec=GearToolkitContext,
        manifest=mocked_manifest,
        client={mocked_destination_id: mocked_acquisition("project")},
        destination={"id": mocked_destination_id},
    )


FWV0 = Path.cwd()


@pytest.fixture
def install_gear_results():
    def _method(zip_name, gear_output_dir=None):
        """Un-archive gear results to simulate running inside a real gear.

        This will delete and then install: config.json input/ output/ work/ freesurfer/

        Args:
            zip_name (str): name of zip file that holds simulated gear.
            gear_output_dir (str): where to install the contents of the zipped file
        """

        # location of the zip file:
        gear_tests = Path("/src/tests/data/")
        if not gear_tests.exists():  # fix for running in circleci
            gear_tests = FWV0 / "tests" / "data/"

        # where to install the data
        if not gear_output_dir or not Path(gear_output_dir).exists():
            gear_output_dir = FWV0

        print("\nRemoving previous gear...")

        if Path(gear_output_dir / "config.json").exists():
            Path(gear_output_dir / "config.json").unlink()

        for dir_name in ["input", "output", "work", "freesurfer"]:
            path = Path(gear_output_dir / dir_name)
            if path.exists():
                print(f"shutil.rmtree({str(path)}")
                shutil.rmtree(path)

        print(f'\ninstalling new gear, "{zip_name}"...')
        unzip_archive(gear_tests / zip_name, str(gear_output_dir))

        # The "freesurfer" directory needs to have the standard freesurfer
        # "subjects" directory and "license.txt" file.

    return _method


@pytest.fixture
def search_caplog_contains():
    def _method(caplog, find_me, contains_me=""):
        """Search caplog message for find_me, return true if it contains contains_me"""

        for msg in caplog.messages:
            if find_me in msg:
                if contains_me in msg:
                    return True
        return False

    return _method


@pytest.fixture
def check_for_fw_key():
    def _method(user_json):
        """Check for FW's API key in $HOME/.config/flywheel/user.json.

        Check that there is a $HOME/.config/flywheel/user.json file, and that it
        contains a "key" entry (for FW's API). If not found, the test using this
        fixture is skipped.
        """

        if not user_json.exists():
            TestCase.skipTest("", f"{str(user_json)} file not found.")

        # Check API key is present:
        with open(user_json, "r", encoding="utf8") as f:
            j = json.load(f)
        if "key" not in j or not j["key"]:
            TestCase.skipTest("", f"No API key available in {str(user_json)}")

    return _method
