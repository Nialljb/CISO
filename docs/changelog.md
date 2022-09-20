# Changelog

## 1.0.3_0.15.4

The previous version failed when you passed the FreeSurfer license either as an input
file or as a config value (string) because the keys they were assigned to did not match
what the GearToolKit expects.

## 1.0.2_0.15.4

The previous version crashed because the `poetry install` was installing packages
independently of the base image Python environment (`conda`), so some `qsiprep` calls
couldn't find packages that actually were in the `conda` environment.

The current version runs `poetry export` to export the poetry dependencies into a
`requirements.txt` file, and uses `pip install` (using the `pip` version that `conda`
uses in the base image) to install them.

The only potential problem is that, because the gear dependencies were resolved by
`poetry` outside the base image, there might be (there are) conflicts between the base
image dependencies and the gear dependencies. In this particular case, `scipy` versions
conflicted. So I had to force `pip` to install the newer version of `scipy` required by
the gear.

## 1.0.1_0.15.4

It was decided that, since QSIprep only runs at the `participant` level, the gear will
only be allowed to run at the subject or at the session level. If the user needs to run
it on multiple subjects, they will need to be run one at a time.

In the future we might support running the gear at the project level, which would
batch-run gears for each subject (with the option to skip if it has already been run).

## 0.2.0

Nate: Decided to add a changelog to keep more informal information about design
decisions.  This is not required for every MR, but is strongly encouraged when a big
change or design change is made.  The more formal description of changes would live in
the `docs/release_notes.md` doc.
