FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONUTF8=1 DATA_DIR=/app/data
WORKDIR /app
COPY bot.py main.py course.py grammar.py i18n.py ./
RUN mkdir -p /app/data
CMD ["python", "-u", "main.py"]
