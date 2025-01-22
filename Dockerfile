#FROM python:3.9-bullseye
FROM lpnhe/grand_proto:latest

WORKDIR /app

# Install dependencies
#RUN  apt update && apt-get install -y gcc libpq-dev netcat && \
#    apt-get clean && pip install --upgrade pip && rm -rf /var/lib/apt/lists/*

# Copy files into the container
COPY . .

COPY wait-for-it.sh /usr/local/bin/wait-for-it

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# execution command
CMD ["wait-for-it", "db", "--", "python", "app.py"]

