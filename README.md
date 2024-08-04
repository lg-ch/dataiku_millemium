# Dataiku Millenium Falcon Graph

The purpose of this project is to provide an application that addresses the challenge described by the [Millenium Falcon Challenge](https://github.com/dataiku/millenium-falcon-challenge).

## Installation

To get started with this project, follow these installation instructions:

1. **Clone the Repository**: First, clone the repository to your local machine.

   ```bash
   git clone https://github.com/lg-ch/dataiku_millemium.git
   cd dataiku_millenium/src
   ```

2. **Build the Docker Image**:  build the Docker image using the following command:

   ```bash
   docker build -t millenium .
   ```

3. **Configure Docker Volume**: You need to select a volume for the docker-compose.yml, particularly for the SQLite database file. 
   If the directory containing your database file yourfile.db is named test_data and is located at the root of the project,
   you can specify the volume as follows:

   ```bash
   volumes:
    - ./test_data:/app/data
   ```
   
   **Note**: The working directory inside the Docker container is /app. Therefore, in your millenium.json file, refer to your database file as data/yourfile.db.

4. **Launch Docker Compose**: At the root of the project, start the services using `docker-compose`.

   ```bash
   docker-compose up -d
   ```
5. **Navigate to the URL** : Open your web browser and go to http://127.0.0.1:8000. You are now at the home page, you can now drag and drop your files and compute the Odds.
   
   **Disclaimer**: The application displays the graph on the screen. However, if the graph is too large, only a portion of it will be displayed for clarity.
   Currently, the application displays a maximum of 12 nodes and 25 edges. (Obviously your files and the computed odds remain the same).

## Using the Command Line Interface (CLI)

To use the CLI, you can execute the command directly from the project's root directory by installing the click python package and run the command as follows:

```bash
pip install click==8.1.7
python3 r2d2_c3po_brain.py r2d2 test_data/millenium.json test_data/empire2.json
```

Ensure that the paths to your `millenium.json`, `empire.json` and `universe.db` files are accessible. 

If you have imported your files into the Docker volume, you can also run the command within the Docker container :

```bash
docker exec -it chewbackah sh
python3 r2d2_c3po_brain.py r2d2 data/millenium.json data/empire2.json
```


   

   
