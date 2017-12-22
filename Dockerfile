From ubuntu:xenial

RUN apt-get update && apt-get install -y \
    build-essential \
    ca-certificates \
    gcc \
    git \
    python-pip \
    python2.7 \
    python2.7-dev \
    ssh \
    python-tk \
    fsl-5.0-core \
    && apt-get autoremove \
    && apt-get clean

RUN pip install -U "setuptools"
RUN pip install -U "pip"
RUN pip install -U "matplotlib"
RUN pip install -U "nibabel"
RUN pip install -U "numpy"
RUN pip install -U "scipy"
RUN pip install -U "scikit-image==0.13.1"

RUN mkdir FeenICS_container
RUN git clone https://github.com/eziraldo/FeenICS.git /FeenICS_container/

ENV PATH $PATH:/FeenICS_container/bin:/usr/share/fsl/5.0
ENV PYTHONPATH $PYTHONPATH:/FeenICS_container/bin

RUN echo "source /etc/fsl/5.0/fsl.sh" >> /root/.bashrc

RUN chmod +x /FeenICS_container/bin/s*

ENTRYPOINT ["/bin/bash"]
