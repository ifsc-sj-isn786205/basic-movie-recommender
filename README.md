# Movie Recommendation API

A simple Python Flask application that provides movie recommendations using a third-party API. This application is designed to run on Google Cloud Platform (GCP) Compute Engine.

## Features

- Random movie recommendations
- RESTful API endpoints
- Environment-based configuration

## API Endpoints

- `GET /` - API information and available endpoints
- `GET /recommend` - Get a random movie recommendation

## Setup Instructions

### Local Development

1. **Clone or download the project files**

2. **Create/join the virtual environment**
   ```bash
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup you environment variables:**

The application uses the following environment variables:

- `API_URI`: The API you are using (e.g. https://www.omdbapi.com/)
- `API_KEY`: Your API key (e.g. an OMDb key that you got from https://www.omdbapi.com/)

5. **Run the application:**
   ```bash
   python main.py
   ```

6. **Test the API:**
   ```bash
   # Random recommendation
   curl http://localhost:8080/recommend
   ```

### GCP Compute Engine Deployment

1. **Create a VM instance:**
   ```bash
   gcloud compute instances create movie-recommender \
     --zone=us-central1-a \
     --machine-type=e2-micro \
     --image-family=ubuntu-2004-lts \
     --image-project=ubuntu-os-cloud \
     --tags=http-server,https-server
   ```

2. **SSH into the instance:**
   ```bash
   gcloud compute ssh movie-recommender --zone=us-central1-a
   ```

3. **Install Python and dependencies:**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip git -y
   ```

4. **Upload your project files to the VM:**
   ```bash
   # From your local machine
   gcloud compute scp --recurse /path/to/isn-api movie-recommender:~/ --zone=us-central1-a
   ```

5. **On the VM, install dependencies and run:**
   ```bash
   cd isn-api
   pip3 install -r requirements.txt
   python3 main.py
   ```

6. **Configure firewall to allow traffic:**
   ```bash
   gcloud compute firewall-rules create allow-movie-api \
     --allow tcp:8080 \
     --source-ranges 0.0.0.0/0 \
     --target-tags http-server
   ```

7. **Access your API:**
   ```bash
   # Get the external IP
   gcloud compute instances describe movie-recommender --zone=us-central1-a --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
   
   # Test the API
   curl http://EXTERNAL_IP:8080/recommend
   ```

### Running as a Service

To run the application as a systemd service on GCP:

1. **Create a service file:**
   ```bash
   sudo nano /etc/systemd/system/movie-recommender.service
   ```

2. **Add the following content:**
   ```ini
   [Unit]
   Description=Movie Recommendation API
   After=network.target

   [Service]
   Type=simple
   User=ubuntu
   WorkingDirectory=/home/ubuntu/isn-api
   ExecStart=/usr/bin/python3 main.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start the service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable movie-recommender
   sudo systemctl start movie-recommender
   sudo systemctl status movie-recommender
   ```

## Example Usage

### Random Recommendation
```bash
curl http://your-server:8080/recommend
```

Response:
```json
{
  "title": "The Dark Knight",
  "year": "2008",
  "genre": "Action, Crime, Drama",
  "plot": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham...",
  "director": "Christopher Nolan",
  "actors": "Christian Bale, Heath Ledger, Aaron Eckhart",
  "rating": "9.0",
  "poster": "https://m.media-amazon.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1_SX300.jpg",
  "imdb_id": "tt0468569",
  "recommendation_reason": "Random recommendation"
}
```
