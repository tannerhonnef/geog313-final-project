# GEOG 313 Final Project
This README describes how to run a container using the dockerfile and executing the notebook that is created as a part of the assignment.

## How to Run
- Set up a new image using the `environment.yml` file.
- This environment has all of the necessary packages necessary to run the code in this project.
- Build the image using the command below.  The . is telling docker to look for the `environment.yml` file in your current working directory. 
```
docker build -t ndvi-lstv .
```
- Run a container from the image `ndvi-lstv` using the command below mounting to your current working directory
```
docker run -p 8888:8888 -p 8787:8787 -v $(pwd):/home/assignment ndvi-lstv
```
- If Jupyter lab does not automatically launch copy the last link into the browser
- Make sure to run code blocks
- When you save the file in the docker container, it will also save to the pwd when you ran the container 
