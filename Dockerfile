FROM python:3

WORKDIR /usr/src/app
RUN apt-get update && apt-get install --no-install-recommends --yes cmake && rm -rf /var/lib/apt/lists/*a

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 1234
CMD [ "python", "./main.py" ]