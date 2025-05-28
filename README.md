## BBSR Challenge Team 4

### What is this?
This repo is part of the N3xtcoder Hackathon Program [**AI for impact**](https://n3xtcoder.org/events/jr84xhaer_ai-for-impact-the-programme-for-changemakers-phase-2) and shows the approach of team 4 to the 
BBSR challenge, Goal 2.

### What is it for?
Architects (and other people) planning a new building can use the tool [eLCA](https://www.bauteileditor.de/) to retrieve 
information about the materials they are using. In this tool, every available material has a unique identifier - a 
UUID. This UUID is referenced in another dataset, tBaustoff, that has crucial information regarding the material's 
life cycle assessment. Unfortunately, the UUID mapping within the tool itself and from the tool to the dataset in 
incomplete and requires a lot of manual research by the users.

The app we developed here uses a sentence transformer Model ([all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2))
to semantically match unmapped entries in the original dataset and automatically look up relevant data in the tBaustoff
dataset.
### How do I get the app running?

**There is a deployed version of the app running on MS Azure. Find it [here](https://bbsr-team4-v4.azurewebsites.net).**

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
1. Make sure you have [poetry](https://github.com/python-poetry/poetry) installed
2. Get the app data to you local machine (see point 1 below "With Docker")
3. Use the terminal to go into the directory where you saved the app data and enter `poetry install`. This installs all needed packages and creates a virtual environment for the project.
4. Activate the environment you just created by entering in your terminal `poetry env activate` and then entering the line poetry just replied to you.
5. Enter `poetry run uvicorn app.main:app`

**With and without Docker**

The app then runs in your browser at http://127.0.0.1:8000.
You can find the running app here: http://127.0.0.1:8000


The API can be reached at `127.0.0.1:8000/api` and has several endpoints:
- `/materials/{uuid}` let's you query specific material UUIDs and returns a matching generic material UUID
- `/update` looks for updates of the Ökobaudat dataset
- `/dataset_info` returns the used dataset and the time it was last updated
- API docs are at `127.0.0.1:8000/docs`
