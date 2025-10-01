# Deployment Guide

## Frontend Deployment to Vercel

### Prerequisites
- A Vercel account ([sign up here](https://vercel.com/signup))
- Your repository hosted on GitHub, GitLab, or Bitbucket
- A deployed backend API (the Python FastAPI backend needs to be hosted separately)

### Steps to Deploy

#### Option 1: Deploy via Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**
   - Visit [vercel.com](https://vercel.com) and log in
   - Click "Add New Project"

2. **Import Repository**
   - Select your Git provider (GitHub/GitLab/Bitbucket)
   - Choose the `Interview-Coach` repository
   - Click "Import"

3. **Configure Project**
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `interview-coach`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
   - **Install Command**: `npm install` (default)

4. **Environment Variables**
   Add the following environment variable:
   - **Name**: `NEXT_PUBLIC_API_BASE`
   - **Value**: Your backend API URL (e.g., `https://api.yourdomain.com`)

5. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy your application
   - You'll receive a deployment URL (e.g., `your-app.vercel.app`)

#### Option 2: Deploy via Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Navigate to Frontend Directory**
   ```bash
   cd interview-coach
   ```

3. **Login to Vercel**
   ```bash
   vercel login
   ```

4. **Deploy to Preview**
   ```bash
   vercel
   ```

5. **Deploy to Production**
   ```bash
   vercel --prod
   ```

6. **Set Environment Variables** (if not already set)
   ```bash
   vercel env add NEXT_PUBLIC_API_BASE
   ```
   Then enter your API URL when prompted.

### Post-Deployment Configuration

#### Update Backend CORS Settings
Your FastAPI backend needs to allow requests from your Vercel domain. Update the CORS configuration in your backend to include your Vercel URL:

```python
# In your FastAPI app
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-app.vercel.app",  # Add your Vercel domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### Environment Variables by Environment

Vercel supports different environment variables for different environments:
- **Production**: Used for your production domain
- **Preview**: Used for preview deployments (e.g., pull requests)
- **Development**: Used for local development with `vercel dev`

You can set these in the Vercel dashboard under Project Settings → Environment Variables.

### Continuous Deployment

Once set up, Vercel automatically:
- Deploys to production when you push to your main/master branch
- Creates preview deployments for pull requests
- Provides deployment previews with unique URLs

### Monitoring and Logs

- **View Deployments**: Go to your project dashboard on Vercel
- **View Logs**: Click on any deployment to see build and runtime logs
- **View Analytics**: Vercel provides built-in analytics for your application

### Troubleshooting

#### Build Fails
- Check the build logs in the Vercel dashboard
- Ensure all dependencies are in `package.json`
- Verify the Node.js version is compatible (Vercel uses Node 18+ by default)

#### API Connection Issues
- Verify `NEXT_PUBLIC_API_BASE` is set correctly
- Check that your backend API is accessible from Vercel's infrastructure
- Ensure CORS is properly configured on your backend

#### Environment Variable Not Working
- Remember that `NEXT_PUBLIC_*` variables are embedded at build time
- After changing environment variables, trigger a new deployment
- For sensitive data, use server-side environment variables (without `NEXT_PUBLIC_` prefix)

### Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment Documentation](https://nextjs.org/docs/deployment)
- [Vercel Environment Variables Guide](https://vercel.com/docs/concepts/projects/environment-variables)

## Backend Deployment

The Python FastAPI backend needs to be deployed separately. Consider these options:

- **Railway**: Python-friendly PaaS with PostgreSQL support
- **Render**: Supports Python web services and PostgreSQL
- **Fly.io**: Good for Docker-based deployments
- **AWS/GCP/Azure**: Full-featured cloud platforms
- **Heroku**: Traditional PaaS with Python support

Each platform will require:
- PostgreSQL database (with pgvector extension for embeddings)
- Redis instance
- Environment variables from `server/.env.example`
