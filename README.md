## Installation

To get started with this project, follow these installation instructions:

1. **Clone the Repository**: First, clone the repository to your local machine.

   ```bash
   git clone https://github.com/your-username/millenium.git
   cd millenium
   ```

2. **Build the Docker Image**: Navigate to the root of the project and build the Docker image using the following command:

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
5. **Navigate to the URL** : Open your web browser and go to http://127.0.0.1:8000. You should see the following image:
   
   

   
