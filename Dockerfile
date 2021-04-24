FROM python
COPY requirements.txt ./
COPY chatbot.py ./
RUN pip install pip update
RUN pip install -r requirements.txt
ENV ACCESS_TOKEN=1662439720:AAFoss198aaCfFDP1feQymNfZj8E6FrENBI
ENV HOST=redis-10818.c56.east-us.azure.cloud.redislabs.com
ENV PASSWORD=28tqKqFVkZS74svW7dYqNlAjl93kwXgg
ENV REDISPORT=10818
CMD ["python", "chatbot.py"]