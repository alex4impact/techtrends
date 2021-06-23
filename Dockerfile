FROM python:3.7
LABEL maintainer="Alexandre Carvalho"

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

RUN python init_db.py

# command to run on container start
CMD [ "python", "techtrends/app.py" ]