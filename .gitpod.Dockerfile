FROM ubuntu:18.04
RUN sudo apt-get update && sudo apt-get install -y python3 python3-dev python3-venv build-essential libcurl4-openssl-dev && \
    sudo apt-get install -y --no-install-recommends curl && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    sudo ln -sf /usr/bin/python3 /usr/bin/python && \
    python get-pip.py && pip install --upgrade pip && \
    rm -rf get-pip.py && \
    pip install jupyterlab && jupyter-notebook -y --generate-config && \
    echo "c = get_config()" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.ip = '*'" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.open_browser = False" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.port = 8888" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.allow_root = True" >> ~/.jupyter/jupyter_notebook_config.py && \
    mkdir -p $workTools && mkdir -p $workData && mkdir -p $workResults && mkdir -p $workTemp && \
    sudo apt-get purge --autoremove -y curl && \
    sudo apt-get autoremove
