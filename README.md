## BBSR Challenge Team 4

This repo is part of the N3xtcoder Hackathon Program [**AI for impact**](https://n3xtcoder.org/events/jr84xhaer_ai-for-impact-the-programme-for-changemakers-phase-2) and shows the approach of team 4 to the BBSR challenge, Goal 2.

Detailed instructions to run the app.

**With Docker**
    
1. Get the app data to you local machine
    - if you have git installed, go to the directory where you want the data, open a console and enter `https://github.com/n3xtcoder-ai4impact/bbsr_challenge_team4.git`. You may be asked for credentials to log in to GitHub.
    - without git, you can download the data by hand. Got to https://github.com/n3xtcoder-ai4impact/bbsr_challenge_team4, click on the green rectangle on the top right, then `Download Zip`. Unpack it where you want it.

2. Install [Docker](https://www.docker.com/get-started/)
    - Docker Desktop: Probably the easiest way. Install it, then follow the instructions in the app to create your local container and run the app.
    - Non-desktop version: There is a different way to install it for every operating system - find it and follow it.

3. Create container and run the app
    - Docker Desktop: Follow the instructions within the app
    - Non-Desktop version: Open a terminal window and navigate to the directory to which you cloned/extracted the app data in step 1. Enter `docker build -t bbsr_challenge_team4 .` to build the container when you run it the first time. To run the app, enter `docker run -d -it -p8000:8080 bbsr_challenge_team4`

**Without Docker**
- make sure you have [poetry](https://github.com/python-poetry/poetry) installed
- create a virtual environment for the project
- run `poetry run uvicorn app.main:app` in your local repo directory

**With and without Docker**

The app then runs in your browser at http://127.0.0.1:8000.
You can find the only available html page here: http://127.0.0.1:8000/input
