"""Module to test parser.py"""

import logging
from os import path as op
from os import symlink
from pathlib import Path

from utils import dry_run


def test_make_dirs_and_files(tmpdir):
    """Tests make_dirs_and_files"""

    # test with a string and with a Path:
    files = [str(tmpdir / "foo" / "bar.txt"), tmpdir / "foo" / "fam" / "bar.txt"]

    dry_run.make_dirs_and_files(files)

    assert [op.exists(f) for f in files]


def test_pretend_it_ran(tmpdir, caplog, search_caplog_contains, mocked_gear_options):
    """Tests for pretend_it_ran"""

    logging.getLogger(__name__)
    caplog.set_level(logging.INFO)

    mocked_gear_options["dry-run"] = True
    mocked_gear_options["work-dir"] = Path("")
    mocked_gear_options["analysis-level"] = "participant"

    mocked_app_options = {"foo": "bar"}

    # pretend_it_ran will create the folders "work" and "output" in the WORKDIR
    # (/flywheel/v0). So that the files created there are deleted after running the
    # test, link those folders to "tmpdir"
    expected_folders = ["work", "output"]
    for ef in expected_folders:
        symlink(ef, tmpdir / ef)

    dry_run.pretend_it_ran(mocked_gear_options, mocked_app_options)

    for msg in ["Executing command", "Creating fake output"]:
        assert search_caplog_contains(caplog, msg)
    assert [op.exists(ef) for ef in expected_folders]
    assert op.exists(
        op.join(
            "output",
            mocked_gear_options["destination-id"],
            "somedir",
            "sub-TOME3024.html",
        )
    )
