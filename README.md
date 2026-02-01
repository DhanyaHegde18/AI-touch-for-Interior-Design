InterioAI – AI Based Interior Design System

InterioAI is a full-stack AI application that generates interior design concepts from user-uploaded room images.  
The system allows users to visualize modern interior designs, get furniture suggestions, and estimate costs using artificial intelligence.


 Features

- Upload a room image and select design preferences
- AI-based interior design generation
- Furniture recommendations based on room type
- Cost estimation for selected furniture
- User authentication and design history
- RESTful API-based backend architecture


 Technologies Usedf
 Frontend
- HTML
- CSS
- JavaScript

Backend
- Python
- Flask (RESTful API framework)
- SQLite Database

AI & Image Processing
- Stable Diffusion (Image-to-Image generation)
- ControlNet (Structure preservation)
- Computer Vision concepts (YOLO, MiDaS – conceptual)


 Project Architecture

- Frontend communicates with backend using REST APIs
- Flask backend handles user requests, image uploads, and AI processing
- AI models generate redesigned interior images
- Results are returned and displayed on the frontend


 Main API

- POST `/api/generate`  
  Generates an AI-based interior design image from the uploaded room photo and user preferences.


 Deployment

- Backend and frontend are deployed as a single Flask application
- REST APIs are hosted on cloud (Render)
- AI inference (Stable Diffusion) is executed locally due to GPU requirements


Academic Note

This project is developed as part of an academic mini/major project to demonstrate the practical application of Artificial Intelligence, Computer Vision and Web Technologies in interior design automation.
