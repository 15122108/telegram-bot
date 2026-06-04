FROM python:3.12-slim

WORKDIR /app

COPY bot.py admin_panel.py start_koyeb.py ./

ENV PYTHONUNBUFFERED=1
ENV DATA_DIR=/data

EXPOSE 8080

CMD ["python", "start_koyeb.py"]
