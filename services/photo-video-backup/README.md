# Photo and Video Backup
This service is used to backup the photos and videos from the IAIF ITB Soccer Google Drive to Facebook.

## Requirements
- Python 3.10
- pip

## Installation
1. Clone the repository
2. Virtual Environment
    - Create a virtual environment
    ```bash
        python -m venv venv
    ```
    - Activate the virtual environment
    ```bash
        source venv/bin/activate
    ```
3. Install the requirements
    ```bash
        pip install -r requirements.txt
    ```

## How to run
1. Run the service
    ```bash
        python main.py
    ```


## Authentication
On the first run, the service will ask for the authentication and prompted user to login using their Google Account. Then we will save the token in the `token.json` file.

While the token is valid, the service will not asking for the authentication.

You need to enable the Google Drive API in order to access the Google Drive and configure the oauth 2.0 credentials in order to get the access token. Follow this guidelines https://developers.google.com/drive/api/quickstart/python

## To do
1. Integrate GDrive API with Facebook API. Download file from Gdrive and upload to Facebook page.
2. Current main functionality (except video upload) is working.
    - Post message to Facebook page
    - Upload photos to Facebook page
    - Access GDrive files

## Issues
1. Facebook video upload had unresolved bug stated in here https://developers.facebook.com/community/threads/821620743399346/ 😭