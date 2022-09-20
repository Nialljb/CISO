ARG BASE

# hadolint ignore=DL3006
FROM ${BASE}

ENV FLYWHEEL="/flywheel/v0"

# Install dev dependencies:
RUN poetry export -f requirements.txt --dev --without-hashes -o $FLYWHEEL/dev-requirements.txt \
    && pip install --no-cache-dir -r $FLYWHEEL/dev-requirements.txt

ENTRYPOINT [""]
