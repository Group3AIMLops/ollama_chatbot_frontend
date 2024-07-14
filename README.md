<!-- ABOUT THE PROJECT -->
## About The Project

This repository is a frontend part of Customer Conversational Intelligence Platform Powered by an LLM Agent. This is created with help of streamlit [![streamlit][streamlit-image]][streamlit-url]

<!-- GETTING STARTED -->
## Getting Started

You can run this locally as either as a python app or as a docker container.

## Running without docker

### Create virtual Environment
```
Follow below steps:

$ git clone https://github.com/Group3AIMLops/ollama_chatbot_frontend.git
$ cd ollama_chatbot_frontend
$ python -m venv venv     or  python -m venv <Project_Path>\venv
```

### Activate Python virtual Environment
```
$ ./venv/Scripts/activate 
```

### Create .env file

```
create .env file with below data

backend_ip = 'http://127.0.0.1' (ip of your backend app)
backend_port = '8001' (port of your backend app)
use_sql = False (False if you dont want to connect to database)
```

### Install dependencies

```
$ pip install -r requirements.txt
```

### Run the application

```
You can run app with below command

$ streamlit run api/app.py
```

## Running with docker

Make sure you have installed docker

### Pull docker image

```
$ docker image pull sumanthegdedocker/chatbot_frontend:latest
```

### Run docker image

```
docker run -d -e use_sql="False" -e backend_ip="http://host.docker.internal" -e backend_port="8001" --add-host host.docker.internal:host-gateway -p 8501:8501 sumanthegdedocker/chatbot_frontend:latest
```


<!-- MARKDOWN LINKS & IMAGES -->
[streamlit-image]: https://docs.streamlit.io/logo.svg
[streamlit-url]: streamlit.io
