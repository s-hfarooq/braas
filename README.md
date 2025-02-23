# "BRaaS: Brainrot as a service

A web app that generates endless short-form video content using AI, similar to TikTok/Instagram Reels/YouTube Shorts.

This was a project for LofiHack 2025: 

## Features
- Infinite scroll video feed
- AI-generated video content

When you scroll, app sends a request to the backend to genererate a prompt for a video.
Backend then sends that prompt to the video generation service to generate a video.
That video is then stored in the Basic.tech database and the app displays it.

## Tech Stack
- React + TypeScript frontend
- Basic.tech API integration for video storage and retrieval
- OAuth2 authentication flow (not fully implemented)

## Setup

1. Clone the repository
2. Install dependencies: 
```
npm install
pip install -r requirements.txt
```
3. Create a `.env` file in the `app` directory with your Basic.tech credentials:
```
VITE_BASIC_PROJECT_ID=your_project_id
VITE_BASIC_API_KEY=your_api_key
```
4. This was for a hackathon project, so we didn't build the full oath flow, so you must grab your JWT manually via:
```
python3 microservices/common/auth.py
```
5. Add the JWT to the `.env` file in the `app` directory:
```
VITE_BASIC_JWT=your_jwt
```

6. Fill out your secrets.json file with the same basic.tech credentials as the .env file.

7. Start the app:
```
docker compose up
```
