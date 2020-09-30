FROM python:3.8
LABEL maintainer "Travis F. Collins <travis.collins@analog.com>"
USER root
WORKDIR /app
ADD . /app
ADD telemetry /app/dash/telemetry
RUN pip install -r requirements_dev.txt
EXPOSE 8050
CMD ["python", "/app/dash/index.py"]
