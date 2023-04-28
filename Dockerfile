#name of the image that we are going to use, base image. 
#hub.docker.com -- Search for python and you can see the images available. 
FROM python:3.9-alpine3.13 
#Person that is going to be maintaining the docker image, best practice so that other people who works in the 
#project knows who the mantainer is.
LABEL maintainer="morera900@gmail"

#Recommended when working with a docker container, 
#Tells python that we do not want to buffer the output. The output will be printed directly to the console, avoiding delays. 
ENV PYTHONUNBUFFERED 1


ARG DEV=false
#Copy current local location of the file/folder -- where is it going. 
COPY ./requirements.txt /tmp/requirements.txt 
COPY ./requirements.dev.txt /tmp/requirements.dev.txt 
COPY ./app /app
#working directory, default directory where out command are going to be run inside our docker image. 
WORKDIR /app 
#expose port 8000 of our container to our machine. 
#Allows access.
EXPOSE 8000



#Runs a command in our alpine image that we are using when building our image.
#Meaning of the commands line by line: 
#Creates a new virtual environment that we are going to use to build out dependencies. 
#Specify the full path of out virtual environment, upgrade pip for the venv that we just created. 
#We install the list of requirements in out docker image. 
#We remove the tmp directory, to delete dependencies, keeping it lightweight, saving space. 
#adds a new user inside our image, best practice not to use the root user. If this is not specified, the only user
#available in alpine image is the root user. Root user has full access. 
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ $DEV = "true"]; \
        then /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    rm -rf /tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

#Updates the environment variable inside our image, So that we dont need to specify the full path of the venv. 
ENV PATH="/py/bin:$PATH"
#Last line in the docker file. The instructions before are going to be run by the root user, but after this are
#going to be run by the django user. 
USER django-user