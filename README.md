# HelpBot Project

## Overview
HelpBot is a project designed to enable website users to create their own virtual assistants. These assistants can be customized with a knowledge base and integrated into websites to perform support functions, enhancing the user experience by providing automated assistance.


## Features
- **Create Assistants**: Easily create virtual assistants tailored to your specific needs.
- **Knowledge Base**: Add and manage files to build a comprehensive knowledge base for your assistants.
- **Website Integration**: Seamlessly integrate assistants into your website to provide automated support to users.
- **Support Functions**: Assistants can handle various support tasks, improving the efficiency of your customer service.


## Technologies Used
- **Languages**: Python, JavaScript/WebComponents, SCSS/Bootstrap
- **Frameworks/Libraries**: 
  - Backend: `starlette`, `aiofiles`, `websockets`, `uvicorn`
  - Frontend: `starlette`, `jinja2`
- **Other Tools**: 
  - Docker: For containerization and orchestration
  - Nginx: For web server and reverse proxy


## Architecture
The project is organized into multiple services, each running in its own Docker container:
- **Backend/API Service (`app-api`)**: Handles API requests and business logic.
- **Frontend Service (`app-web`)**: Serves the web interface.
- **Nginx**: Acts as a reverse proxy and load balancer.
- **OAuth2 Proxies**: For authentication via Google and GitHub.


## Getting Started

### Prerequisites
- Docker
- Docker Compose

### Installation
1. Clone the repository:
```sh
git clone https://github.com/gansik/akira-release.git
cd akira-release
```
2. Set up environment variables in a .env file
3. Build and start the services:
```sh
docker-compose up -d
```

### Usage

Access the application at https://localhost (or the configured domain).

## Misc

### Regenerate CSS styles by SCSS files of Bootstrap
```sh
    sudo docker build --tag bootstrap ./bootstrap
    sudo docker run -p 0.0.0.0:3000:3000 bootstrap server
    sudo docker run bootstrap css-lint
    sudo docker run -v ./bootstrap/scss:/app/scss:ro -v ./volumes/html/_/bs:/app/css bootstrap css-compile

```

### Run Backend/API Service without docker
```sh
    cd ./app-api
    poetry shell
    uvicorn app.main:app --reload
```

### Run Frontend Service without docker
```sh
    cd ./app-web
    poetry shell
    uvicorn app.main:app --reload
```

### Renew certs (webroot dir is `/var/www/certbot`)
```sh
    sudo docker compose run --rm certbot certonly -d ai.ioix.net --webroot
```

