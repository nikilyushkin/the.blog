FROM ubuntu:23.10

ENV PIP_NO_CACHE_DIR=true
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PIP_DISABLE_PIP_VERSION_CHECK=true
ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_BREAK_SYSTEM_PACKAGES=1

RUN date

RUN apt-get update \
    && apt-get install --no-install-recommends -yq \
      build-essential \
      python3 \
      python3-dev \
      python3-pip \
      libpq-dev \
      make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip3 install tzdata
RUN pip3 install pytz
RUN pip3 install poetry --break-system-packages
RUN poetry install --no-interaction --no-ansi

CMD ["make", "docker-run-production"]
