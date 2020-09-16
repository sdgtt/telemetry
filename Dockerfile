FROM python:3.8
LABEL maintainer "Travis F. Collins <travis.collins@analog.com>"
USER root
WORKDIR /web
ADD . /web
RUN pip install -r requirements.txt
EXPOSE 8050
CMD ["python", "./web/index.py"]
