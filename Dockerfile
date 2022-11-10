FROM nialljb/ciso:latest
# flywheel/fw-gear-ants-base:2.3.5 
ENV HOME=/root/

ENV FLYWHEEL="/flywheel/v0"
#RUN mkdir -p $FLYWHEEL/input
WORKDIR $FLYWHEEL

# Dependencies - some possibly dev dependencies - to run this.
# Install git to run pre-commit hooks inside container:
# RUN apt-get update && \
#     apt-get install --no-install-recommends -y software-properties-common=0.96.20.2-2 && \
#     apt-get clean && \
#     pip3 install --no-cache-dir "poetry==1.1.11" && \
#     rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Installing the current project (most likely to change, above layer can be cached)
COPY ./ $FLYWHEEL/

# Installing main dependencies
# RUN poetry install --no-dev
# RUN pip3 install --no-cache-dir -r $FLYWHEEL/requirements.txt

# Configure entrypoint
RUN chmod a+x $FLYWHEEL/run.py

ENTRYPOINT ["poetry","run","python","/flywheel/v0/run.py"]
