## BBSR Challenge Team 4

How to run the app:
- locally: `poetry run uvicorn app.main:app`
- in docker: 
    - (needs [Docker](https://www.docker.com/get-started/) installed on your machine)
    - to build: `docker build -t bbsr_challenge_team4 .`
    - to run: `docker run -d -it -p8000:8080 bbsr_challenge_team4`

The app then runs at http://127.0.0.1:8000.
You can find the only available html page here: http://127.0.0.1:8000/input