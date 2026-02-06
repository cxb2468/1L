# Flask Japan Vocabulary Application - Production Deployment Guide

## Overview

This document explains how to deploy the Flask Japan Vocabulary application in a production environment on Windows 11 using Waitress as the WSGI server.

## Prerequisites

- Windows 11
- Python 3.8 or higher
- Administrative privileges (for service installation)

## Deployment Steps

### 1. Setup Directory Structure

The application files should be placed in `D:\1L\deployment`.

### 2. Create Virtual Environment

```cmd
cd D:\1L\deployment
python -m venv venv
```

### 3. Activate Virtual Environment and Install Dependencies

```cmd
D:\1L\deployment\venv\Scripts\activate
pip install -r requirements_windows.txt
```

### 4. Configure Environment Variables

Set the following environment variables:
- `FLASK_CONFIG=production`
- `SECRET_KEY=your-production-secret-key-here`
- `DATABASE_URL=japan.db`

### 5. Running the Application

#### Option 1: Automatic Setup and Run (Recommended)

Double-click on `setup_and_run.bat` which will:
- Check Python installation
- Create virtual environment if needed
- Install dependencies
- Start the application

#### Option 2: Manual Start

Double-click on `start_server.bat` or run:

```cmd
start_server.bat
```

#### Option 3: Start with Environment Variables

Double-click on `start_with_env.bat` or run:

```cmd
start_with_env.bat
```

#### Option 4: Command Line

From the deployment directory:

```cmd
D:\1L\deployment\venv\Scripts\activate
waitress-serve --host=0.0.0.0 --port=8000 wsgi:application
```

### 6. Accessing the Application

Once started, the application will be available at:
- http://localhost:8000
- http://127.0.0.1:8000
- http://your-machine-ip:8000 (if accessed from other machines on the network)

### 7. Stopping the Application

#### Option 1: Close the Command Window

Simply close the command window where the application is running.

#### Option 2: Using the Stop Script

Double-click on `stop_server.bat` or run:

```cmd
stop_server.bat
```

## Configuration Files

### Database

The application uses SQLite database (`japan.db`) which is initialized from `japan.xlsx` if not present.

### Nginx (Optional)

For production environments with high traffic, you can use Nginx as a reverse proxy. The configuration file is provided in `nginx.conf`.

## Security Considerations

1. Change the default secret key in production
2. Use a strong password for admin access
3. Consider using HTTPS in production
4. Restrict access to the application if needed by changing the host binding

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## Maintenance

### Updating the Database

To update the database with new data from Excel:
1. Replace `japan.xlsx` with the new file
2. Delete `japan.db`
3. Restart the application (database will be recreated automatically)

### Backing Up Data

Regularly backup the `japan.db` file to prevent data loss.