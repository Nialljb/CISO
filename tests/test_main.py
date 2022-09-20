"""Module to test main.py"""
import logging
import os.path
from pathlib import Path
from unittest.mock import patch

import pytest

from fw_gear_bids_qsiprep import main


# Test 2x2 use cases:
# - run_bids_validation = True/None
@pytest.mark.parametrize("run_bids_validation", [True, None])
# - when there are and when there aren't bids_app_args
@pytest.mark.parametrize("bids_app_args", [None, "arg1 arg2 --my_arg"])
def test_generate_command(run_bids_validation, bids_app_args):
    """Unit tests for generate_command"""

    desired_bids_app_binary = "my_bids_app"
    desired_analysis_level = "medium_rare"
    desired_work_dir = "foo"
    desired_output_analysis_id_dir = "bar"
    gear_options = {
        "bids-app-binary": desired_bids_app_binary,
        "analysis-level": desired_analysis_level,
        "work-dir": Path(desired_work_dir),
        "output_analysis_id_dir": Path(desired_output_analysis_id_dir),
        "run-bids-validation": run_bids_validation,
    }
    app_options = {
        "bids_app_args": bids_app_args,
        "anat-only": True,
        "mem_mb": 10240,
    }

    cmd = main.generate_command(
        gear_options,
        app_options,
    )

    # Check that the returned cmd:
    # - is a list of strings:
    assert isinstance(cmd, list)
    assert all(isinstance(c, str) for c in cmd)
    # starts with the mandatory arguments:
    assert cmd[0:4] == [
        desired_bids_app_binary,
        str(Path(desired_work_dir) / "bids"),
        desired_output_analysis_id_dir,
        desired_analysis_level,
    ]

    # check that the bids_app_args are in the command:
    if bids_app_args:
        assert [arg in cmd for arg in bids_app_args.split()]

    # Check that the other app_options are in the cmd:
    for key, val in app_options.items():
        if key != "bids_app_args":
            if isinstance(val, bool):
                assert f"--{key}" in cmd
            elif isinstance(val, int):
                assert f"--{key}={val}" in cmd
            else:
                if " " in val:
                    assert f"--{key} {val}" in cmd
                else:
                    assert f"--{key}={val}" in cmd

    # Check that if the "run-bids-validation" key is missing from the gear_options,
    # "--skip-bids-validation" is in the returned command:
    if "run-bids-validation" not in gear_options:
        assert "--skip-bids-validation" in cmd

    # TO-DO: Test the verbose level


def test_generate_command_space_separated_argument(mocked_gear_options):
    """Test for the case that an argument value is a space-separated list"""

    space_separated_arg_value = "elem1 elem2 elem3"
    single_arg_value = "single"
    mocked_gear_options["work-dir"] = Path("/foo")
    app_options = {
        "space-separated-option": space_separated_arg_value,
        "single-arg-value": single_arg_value,
    }

    cmd = main.generate_command(
        mocked_gear_options,
        app_options,
    )

    # Check that all app_options are in the cmd:
    for key, val in app_options.items():
        if " " in val:
            assert f"--{key} {val}" in cmd
        else:
            assert f"--{key}={val}" in cmd


def test_prepare(mocked_gear_options):
    """Unit tests for prepare"""

    app_options = {}

    expected_errors = []
    expected_warnings = []

    errors, warnings = main.prepare(mocked_gear_options, app_options)

    assert errors == expected_errors
    assert warnings == expected_warnings


# Test 2 use cases:
# - dry_run = True/False
@pytest.mark.parametrize("dry_run", [True, False])
@patch("fw_gear_bids_qsiprep.main.generate_command")
def test_run(
    mock_generate_command,
    tmpdir,
    caplog,
    search_caplog_contains,
    mocked_gear_options,
    dry_run,
):
    """Unit tests for run

    We test the cases of a dry run and of a successful real run
    """

    logging.getLogger(__name__)
    caplog.set_level(logging.INFO)

    my_cmd = ["echo", "Foo"]
    mock_generate_command.return_value = my_cmd

    # main.run attempts to create the "destination-id" folder, so need to modify the
    # default one:
    foo_gear_options = mocked_gear_options
    foo_gear_options["output-dir"] = tmpdir / foo_gear_options["output-dir"]
    foo_gear_options["output_analysis_id_dir"] = (
        tmpdir / foo_gear_options["output_analysis_id_dir"]
    )
    if dry_run:
        foo_gear_options["dry-run"] = True

    exit_code = main.run(mocked_gear_options, {})

    assert exit_code == 0
    mock_generate_command.assert_called_once()
    assert os.path.exists(foo_gear_options["output_analysis_id_dir"])
    # Check that there is a record in the log with "Executing command" and my_cmd.
    # This shows that "exec_command" was run with the expected command.
    assert search_caplog_contains(caplog, "Executing command", " ".join(my_cmd))


@patch("fw_gear_bids_qsiprep.main.generate_command")
def test_run_error(mock_generate_command, tmpdir, caplog, mocked_gear_options):
    """Unit tests for run when running the command throws an error"""

    logging.getLogger(__name__)
    caplog.set_level(logging.INFO)

    my_cmd = ["ohce", "Foo"]
    mock_generate_command.return_value = my_cmd

    # main.run attempts to create the "destination-id" folder, so need to modify the
    # default one:
    foo_gear_options = mocked_gear_options
    foo_gear_options["output-dir"] = tmpdir / foo_gear_options["output-dir"]
    foo_gear_options["output_analysis_id_dir"] = (
        tmpdir / foo_gear_options["output_analysis_id_dir"]
    )

    # We expect a runtime error:
    with pytest.raises(RuntimeError):
        main.run(mocked_gear_options, {})
