FROM python:3.8



WORKDIR /var/user_stats/
COPY requirements.txt requirements.txt

RUN pip install -U -q pip
RUN pip install -q -r requirements.txt

COPY config.yml config.yml
COPY run.sh run.sh
COPY user_stats.py user_stats.py

EXPOSE 8000

CMD bash /var/user_stats/run.sh