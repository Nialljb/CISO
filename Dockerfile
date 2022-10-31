FROM flywheel/fw-gear-ants-base:2.3.5

ENV HOME=/root/

ENV FLYWHEEL="/flywheel/v0"
WORKDIR $FLYWHEEL

# Dependencies - some possibly dev dependencies - to run this.
# Install git to run pre-commit hooks inside container:
RUN apt-get update && \
    apt-get install --no-install-recommends -y git=1:2.17.1-1ubuntu0.12 && \
    apt-get clean && \
    pip3 install --no-cache-dir "poetry==1.1.11" && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Installing main dependencies
COPY requirements.txt $FLYWHEEL/
RUN pip install --no-cache-dir -r $FLYWHEEL/requirements.txt

COPY fw_gear_ants_ciso $FLYWHEEL/fw_gear_ants_ciso
COPY data ${FLYWHEEL}/input

# Installing the current project (most likely to change, above layer can be cached)
COPY ./ $FLYWHEEL/
RUN pip install --no-cache-dir .

# Configure entrypoint
RUN chmod a+x $FLYWHEEL/run.py

ENTRYPOINT ["poetry","run","python","/flywheel/v0/run.py"]
