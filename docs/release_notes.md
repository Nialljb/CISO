# Release notes

## 1.0.3_0.15.4

__FIX__:

Fix the key names in the manifest to handle the FreeSurfer licenses (for both a file
and a string) to match what the GearToolKit expects.

## 1.0.2_0.15.4

__FIX__:

`Dockerfile`: Fix the fact that `qsiprep` calls couldn't find some of the Python
packages that came with the original base image. It now uses `poetry export` to export
the poetry dependencies into a `requirements.txt` file, and uses `pip install` (using
the `pip` version that `conda` uses in the base image) to install them.

## 1.0.1_0.15.4

__Maintenance__:

Major refactoring, to bring the gear up to the new gear standards in Gitlab:

* Separate parts of the code that are needed to run on a Flywheel instance, rather
than application specific (e.g., where to grab the data, where the outputs should end,
etc.)
* Separate the different parts of the code that are BIDS-app generic from those that
are specific for this App, with the idea that in the future we would work on a BIDS-App
gear class.
* Break the code into smaller functional units, so it is easier to read.
* Try to use auxiliary methods from the Gear Toolkit and bids-client as much as
possible.

## 0.0.1_0.12.2

Initial release, in [GitHub](https://github.com/flywheel-apps/bids-qsiprep/tree/0.0.1_0.12.2)
