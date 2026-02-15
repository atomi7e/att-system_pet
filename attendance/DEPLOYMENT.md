# Deployment Guide

This guide will help you deploy the Attendance Tracking System to a free hosting service.

## Option 1: Render (Recommended - Free Tier Available)

### Steps:

1. **Create a GitHub Repository**
   - Push your code to GitHub
   - Make sure all files are committed

2. **Sign up for Render**
   - Go to https://render.com
   - Sign up with your GitHub account

3. **Create a New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Use these settings:
     - **Name**: attendance-system (or your choice)
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
     - **Start Command**: `gunicorn attendance_system.wsgi:application`

4. **Configure Environment Variables**
   - Go to Environment tab
   - Add these variables:
     ```
     SECRET_KEY=your-secret-key-here (generate a new one)
     DEBUG=False
     ALLOWED_HOSTS=your-app-name.onrender.com
     ```

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your app

### Using render.yaml (Alternative)
- If you included `render.yaml`, Render can auto-detect and use it
- Just connect your repo and Render will configure everything

## Option 2: Railway

### Steps:

1. **Sign up for Railway**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure**
   - Railway will auto-detect Python
   - Add environment variables:
     ```
     SECRET_KEY=your-secret-key
     DEBUG=False
     ```
   - Railway will automatically set ALLOWED_HOSTS

4. **Deploy**
   - Railway will automatically deploy on every push

## Option 3: PythonAnywhere (Free Tier)

### Steps:

1. **Sign up**
   - Go to https://www.pythonanywhere.com
   - Create a free account

2. **Upload Files**
   - Use the Files tab to upload your project
   - Or use Git to clone your repository

3. **Configure Web App**
   - Go to Web tab
   - Click "Add a new web app"
   - Choose Django
   - Set Python version to 3.11
   - Point to your project directory

4. **Configure Settings**
   - Edit WSGI file to point to your project
   - Set ALLOWED_HOSTS in settings.py
   - Run migrations: `python manage.py migrate`
   - Collect static files: `python manage.py collectstatic`

5. **Reload**
   - Click the green "Reload" button

## Important Notes for Production

### Before Deploying:

1. **Generate a new SECRET_KEY**
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

2. **Update settings.py for production:**
   - Set `DEBUG = False`
   - Set `ALLOWED_HOSTS = ['your-domain.com']`
   - Use environment variables for sensitive data

3. **Database:**
   - For production, consider using PostgreSQL (Render and Railway offer free PostgreSQL)
   - Update DATABASES in settings.py if using PostgreSQL

4. **Create Superuser:**
   - After deployment, run: `python manage.py createsuperuser`
   - Or use the admin panel

## Testing Your Deployment

1. Visit your deployed URL
2. Test the home page
3. Test admin panel: `/admin/`
4. Test API endpoints:
   - GET: `https://your-app.com/api/attendance/`
   - POST: `https://your-app.com/api/attendance/mark/`

## API Testing with Postman

### GET Request
- URL: `https://your-app.com/api/attendance/`
- Method: GET
- Query params (optional):
  - `class_id=1`
  - `date=2025-01-18`
  - `student_id=1`

### POST Request
- URL: `https://your-app.com/api/attendance/mark/`
- Method: POST
- Headers: `Content-Type: application/json`
- Body (JSON):
  ```json
  {
    "student_id": 1,
    "class_id": 1,
    "date": "2025-01-18",
    "status": "present"
  }
  ```

### PUT Request
- URL: `https://your-app.com/api/attendance/1/`
- Method: PUT
- Headers: `Content-Type: application/json`
- Body (JSON):
  ```json
  {
    "status": "late",
    "notes": "Updated via API"
  }
  ```

### DELETE Request
- URL: `https://your-app.com/api/attendance/1/`
- Method: DELETE

## Troubleshooting

- **Static files not loading**: Make sure `collectstatic` ran successfully
- **Database errors**: Check migrations were applied
- **500 errors**: Check logs in your hosting platform
- **CORS issues**: Add `corsheaders` if needed for frontend integration

