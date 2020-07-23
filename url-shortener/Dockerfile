FROM python:3.8.3-slim-buster

RUN pip install --upgrade pip
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r /usr/src/app/requirements.txt
RUN pip install --no-cache-dir gunicorn

COPY fcc_url_shortener /usr/src/app/fcc_url_shortener/

EXPOSE 5000

WORKDIR /usr/src/app/
CMD ["gunicorn", "-b", "0.0.0.0:5000", "fcc_url_shortener:app"]