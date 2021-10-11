FROM ubuntu:latest

SHELL ["/bin/bash", "-c"]
ENV DEBIAN_FRONTEND=noninteractive

# Install srtg-watcherstream
RUN apt-get update && apt-get install -y
RUN apt-get install gnupg1 -y
RUN sh -c 'echo deb https://apt.surrogate.tv/ buster main >> /etc/apt/sources.list' && apt-key adv --keyserver "hkps://keys.openpgp.org" --recv-keys "58278AC826D269F82F1AD74AD7337870E6E07980" && apt-get update && apt-get install -y srtg-watcherstream

# Install inotify-proxy
RUN apt-get install -y build-essential git
RUN git clone https://github.com/sillypog/inotify-proxy.git /src/app/setup
RUN cd /src/app/setup && make

# Install supervisor
RUN apt-get install -y supervisor

RUN python3 -m pip install requests

COPY srtg.toml /etc/srtg/srtg.toml
RUN touch /src/app/setup/log.txt
COPY scripts/multiprocess /src/app/setup/run
COPY scripts/srtg-watcherstream /usr/bin/srtg-watcherstream
#COPY scripts/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

WORKDIR /tmp/srtg_hls

#CMD ["python3", "/usr/bin/srtg-watcherstream", "&", "/src/app/setup/bin/inotify-proxy"]

#CMD ["/usr/bin/supervisord"]

CMD ["/src/app/setup/run"]