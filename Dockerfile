FROM pennbbl/qsiprep:0.15.4 as base
# the qsiprep image is huge (11.6 GB). To create the main functionality of the gear,
# just comment out the previous "FROM" line and uncomment this line (to use a vanilla
# Python):
#FROM python:3.8.10-slim-buster as base

LABEL maintainer="support@flywheel.io"

ENV HOME=/root/

ENV FLYWHEEL="/flywheel/v0"
WORKDIR ${FLYWHEEL}

# Install git to run pre-commit hooks inside container:
# (We need to rm cuda & nvidia sources because their keys are broken, and we don't
#  need to update them anyway)
RUN rm /etc/apt/sources.list.d/cuda.list \
       /etc/apt/sources.list.d/nvidia-ml.list && \
    apt-get update && \
    apt-get install --no-install-recommends -y git=1:2.17.1-1ubuntu0.12 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Installing main dependencies
COPY requirements.txt $FLYWHEEL/
RUN pip install --no-cache-dir -r $FLYWHEEL/requirements.txt

# Installing the current project (most likely to change, above layer can be cached)
COPY ./ $FLYWHEEL/
RUN pip install --no-cache-dir .

# Configure entrypoint
RUN chmod a+x $FLYWHEEL/run.py
ENTRYPOINT ["python","/flywheel/v0/run.py"]
