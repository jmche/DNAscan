FROM ubuntu:18.04

ENV workDir /workDir
ENV workTools /workDir/Tools
ENV workData /workDir/Data
ENV workResults /workDir/Results
ENV workTemp /workDir/Temp

RUN apt-get update && apt-get install -y python3 python3-dev python3-venv build-essential libcurl4-openssl-dev && \
    apt-get install -y --no-install-recommends curl && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    ln -sf /usr/bin/python3 /usr/bin/python && \
    python get-pip.py && pip install --upgrade pip && \
    rm -rf get-pip.py && \
    pip install jupyterlab && jupyter-notebook -y --generate-config && \
    echo "c = get_config()" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.ip = '*'" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.open_browser = False" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.port = 8888" >> ~/.jupyter/jupyter_notebook_config.py && \
    echo "c.NotebookApp.allow_root = True" >> ~/.jupyter/jupyter_notebook_config.py && \
    mkdir -p $workTools && mkdir -p $workData && mkdir -p $workResults && mkdir -p $workTemp && \
    apt-get autoremove 

### Gitpod user ###
# '-l': see https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#user
RUN useradd -l -u 33333 -G sudo -md /home/gitpod -s /bin/bash -p gitpod gitpod \
    # passwordless sudo for users in the 'sudo' group
    && sed -i.bkp -e 's/%sudo\s\+ALL=(ALL\(:ALL\)\?)\s\+ALL/%sudo ALL=NOPASSWD:ALL/g' /etc/sudoers
ENV HOME=/home/gitpod
WORKDIR $HOME
# custom Bash prompt
RUN { echo && echo "PS1='\[\e]0;\u \w\a\]\[\033[01;32m\]\u\[\033[00m\] \[\033[01;34m\]\w\[\033[00m\] \\\$ '" ; } >> .bashrc

USER gitpod
RUN mkdir ~/.cache && sh -c "$(curl -fsSL https://raw.githubusercontent.com/Linuxbrew/install/master/install.sh)"
ENV PATH="$PATH:/home/linuxbrew/.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin/" \
    MANPATH="$MANPATH:/home/linuxbrew/.linuxbrew/share/man" \
    INFOPATH="$INFOPATH:/home/linuxbrew/.linuxbrew/share/info" \
    HOMEBREW_NO_AUTO_UPDATE=1
RUN sudo apt-get remove -y cmake \
    && brew install cmake
