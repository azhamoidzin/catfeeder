# catefeeder (Backend)

This project uses Docker Compose to set up and run containers. Follow the instructions below to install Docker and Docker Compose, and to build and run the project.

## Prerequisites

Before getting started, ensure you have the following installed:

- Docker
- Docker Compose

## Installation

### Docker

1. **Download and install Docker:**

   - **Windows/Mac:**
     - Visit [Docker Desktop](https://www.docker.com/products/docker-desktop) and download the installer.
     - Run the installer and follow the on-screen instructions.

   - **Linux:**
     - Follow the instructions specific to your distribution at [Docker's official documentation](https://docs.docker.com/engine/install/).

2. **Verify Docker installation:**

   Open a terminal and run:

   ```bash
   docker --version
   ```

   You should see the Docker version printed out.

### Docker Compose

1. **Install Docker Compose:**

   - Docker Compose is included with Docker Desktop for Windows and Mac.
   - For Linux, follow the official guide: [Install Docker Compose](https://docs.docker.com/compose/install/).

2. **Verify Docker Compose installation:**

   Run the following command:

   ```bash
   docker-compose --version
   ```

   You should see the Docker Compose version printed out.

## Building and Running the Project

1. **Clone the repository:**

   ```bash
   git clone https://github.com/azhamoidzin/catfeeder.git
   cd catfeeder
   ```

2. **Setup configuration**

   Rename `secrets.env.template` file to `secrets.env` and fill required values

3. **Build and run the containers:**

   Execute the following command in the project directory:

   ```bash
   docker-compose up --build
   ```

   This command builds the images and starts the containers as specified in the `docker-compose.yml` file.

4. **Access the application:**

   Once the containers are running, access the application via:

   ```plaintext
   http://localhost:your_port
   ```

   Replace `your_port` with the appropriate port number specified in your `docker-compose.yml` (`8000` by default).
