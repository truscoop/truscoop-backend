FROM python:3.8.5

RUN mkdir usr/app
WORKDIR usr/app

COPY . .

RUN pip install -r requirements.txt

# ENV FLASK_APP=src/app.py

CMD python3 src/app.py

# CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]