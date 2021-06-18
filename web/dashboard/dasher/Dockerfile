FROM python:3.8
LABEL maintainer "Travis F. Collins <travis.collins@analog.com>"
USER root
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
RUN cd telemetry_src && python setup.py install; cd ..
EXPOSE 5000
CMD ["python", "/app/app.py"]
