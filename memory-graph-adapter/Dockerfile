FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn
COPY graph_shape.py adapter.py ./

ENV PORT=8070
EXPOSE 8070
# gunicorn serves adapter.py's `app`; HOST/PORT via adapter.py defaults otherwise.
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT} adapter:app"]
