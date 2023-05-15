FROM tiangolo/meinheld-gunicorn:python3.9

WORKDIR /most

EXPOSE 2222
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_APP=most.tdk.rise
ENV WORKERS_PER_CORE=3

CMD ["flask", "run", "--host=0.0.0.0", "--port=2222"]
