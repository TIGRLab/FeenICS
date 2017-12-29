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
RUN pip install -U "docopt"
RUN pip install -U "glob"
RUN pip install -U "pandas"

RUN mkdir FeenICS
RUN mkdir ICArus

RUN git clone https://github.com/eziraldo/FeenICS.git /FeenICS/
RUN git clone https://github.com/edickie/ICArus.git /ICArus/

ENV PATH $PATH:/FeenICS/bin:/usr/share/fsl/5.0:/ICArus/bin
ENV PYTHONPATH $PYTHONPATH:/FeenICS/bin:/ICArus/bin

RUN echo "source /etc/fsl/5.0/fsl.sh" >> /root/.bashrc

RUN chmod +x /FeenICS/bin/*
RUN chmod +x /ICArus/bin/*

ENTRYPOINT ["/bin/bash"]
