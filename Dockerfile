FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN pip install --upgrade pip
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN apt-get clean && apt-get update
RUN apt-get install -y gconf-service libasound2 libatk1.0-0 libcairo2 libcups2 libfontconfig1 libgdk-pixbuf2.0-0 libgtk-3-0 libnspr4 libpango-1.0-0 libxss1 fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils
RUN python -m playwright install --with-deps chromium
EXPOSE 3000
VOLUME ["/app/data"]    
COPY . .
ENTRYPOINT ["python","app.py"]