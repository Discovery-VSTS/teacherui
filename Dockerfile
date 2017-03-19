FROM python:3.4

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY . .

EXPOSE 8000

WORKDIR /usr/src/app/

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "teacherUI.wsgi", "-b", "0.0.0.0:8000"]
