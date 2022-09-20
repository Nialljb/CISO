# Tests

## Unit tests

To run the unit tests, first follow [these
instructions](../CONTRIBUTING.md#getting-started) to install Poetry and the gear
dependencies.

After that, you can run the tests by calling, from the project top level folder:

```shell
poetry run pytest tests/
```

## Integration tests

The integration tests simulate the run of the gear.

They are run together with the unit tests when running the command above. If you want
to only run the integration tests, but not the unit tests, you can just run:

```shell
poetry run pytest tests/integration_tests
```

## End-to-end tests

The end-to-end tests will do a full run of the gear: using your Flywheel API key and
the information in the corresponding `tests/data/<test_name>.zip` file, they will
download the data in BIDS format, run the `bids-validator` and run the corresponding
`qsiprep` call.

Because they call both the `bids-validator` and `qsiprep`, if you don't have them
installed in your path, the best way to run them is inside the test Docker image:

```shell
base_image_tag=<base_image_tag>
# build the base image:
docker build -t ${base_image_tag} .
# build the test image:
test_image_tag=${base_image_tag}_tests
docker build --build-arg BASE=${base_image_tag} \
    -t ${test_image_tag} \
    -f tests/Dockerfile .
# run the end-to-end tests, by running a docker container that mounts your
# .config/flywheel folder in the container. (Note: they take about 5-6 mins to run.)
docker run --rm \
    -v $HOME/.config/flywheel:/root/.config/flywheel \
    -v $PWD/tests/data:/flywheel/v0/tests/data \
    --entrypoint /bin/bash \
    ${test_image_tag} \
       -c "poetry run pytest -s tests/end-to-end_tests"
```

These are the end-to-end tests:

### test_start_run.py

This test does a real `qsiprep` run, except that it times it out after 3 minutes (can
be changed, if desired). It configures the gear, downloads the data from the Flywheel
instance, bids-validates it and launches the `qsiprep` call, timing out after 3
minutes.

This way, it checks that `qsiprep` and the `bids-validator` are correcting installed.

### test_boilerplate.py

Because the `qsiprep` call in [test_start_run](#test_start_runpy) times out and doesn't
complete successfully, this test runs `qsiprep` with the `--boilerplate` option, which
only generates the boilerplate information, so the run completes fast, and we can test
the post-run part of the gear (writing of metadata, zipping output files to the
expected place, etc.)
