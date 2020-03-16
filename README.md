# Details on Using Python/Zeep with CUCM AXL API
This repo contains details on how to use Python/Zeep along
with the CUCM AXL SOAP API to make Administering the CUCM easier.

Ths repo contains the following information
- Information on installing Python and Zeep
- Sample programs that show off the things you can do


# Getting Started
This application runs a Python Flask App in a Docker Container.

This is done to make the app more portable across systems

# Requirements
Docker (Linux) or Docker Desktop (Mac / Windows) must be installed.  The link below takes you to the Docker website where you can download 

[Docker Desktop](https://www.docker.com/products/docker-desktop)

# Installation

- Install Docker or Docker Desktop and make sure its running
- Clone this Repo or download the file to your local computer in a directory
- Run the command `docker build -t flask-cucm-zeep .` to build the Docker Image
- Run the command `docker run -it --rm --name running-flask-cucm-zeep --p 5000:5000 flask-cucm-zeep` to build and run a container based on the image you just created.

# Accessing the Application
Open your web browser and point it to `http://127.0.0.1:5000`

# Using the Application
Across the top of the page will be a menu of tasks.  Click on a task.  The task will prompt you to provide credentials to your CUCM.  You must provide an IP Address (not hostname), username, and password with permissions to access the AXL Interface in the CUCM.

# Customize the App
If you don't want to have to type your Username and IP Address every time, you can modify the `.env` file.  Then run the `docker build` and `docker run` commands above again and now when you run an app, those values will be prepopulated, so you'll only have to type in the password each time 

# Cleanup
## Stoping the Container
- To stop the container press `Ctrl-C` 

## Deleting the Container
Nothing, the `--rm` flag will automatically delete the container when it's done running.

## Deleting the Image
Type `docker images` will give you a list of all images.

Type `docker image rm flask-cucm-zeep` to remove the image created with the build command.
