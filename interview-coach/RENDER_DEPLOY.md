# Deploying Interview Coach Backend to Render

This guide will help you deploy the Interview Coach FastAPI backend to Render using the included `render.yaml` configuration.

## Prerequisites

1. A [Render](https://render.com) account
2. Fork or push this repository to GitHub (Render deploys from Git repositories)
3. API keys for LLM providers (OpenAI, Anthropic, or local LLM endpoint)

## Quick Deploy

### Option 1: Deploy via render.yaml (Recommended)

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **New** → **Blueprint**
3. Connect your GitHub repository
4. Select the repository containing this code
5. Render will automatically detect the `render.yaml` file
6. Review the services that will be created:
   - PostgreSQL database (with pgvector support)
   - Redis cache
   - FastAPI web service
7. Click **Apply** to create all services

### Option 2: Manual Deployment

If you prefer to set up services manually:

#### 1. Create PostgreSQL Database

1. Go to **Dashboard** → **New** → **PostgreSQL**
2. Name: `interview-coach-db`
3. Database: `interview_coach`
4. User: `interview_coach_user`
5. Plan: Choose based on your needs (Free/Starter)
6. Click **Create Database**

**Note**: For pgvector support, you may need to:
- Use a Render PostgreSQL instance (most plans support extensions)
- Or connect to an external PostgreSQL instance with pgvector installed

#### 2. Create Redis Instance

1. Go to **Dashboard** → **New** → **Redis**
2. Name: `interview-coach-redis`
3. Plan: Choose based on your needs (Free/Starter)
4. Click **Create Redis**

#### 3. Create Web Service

1. Go to **Dashboard** → **New** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `interview-coach-api`
   - **Runtime**: Docker
   - **Region**: Choose your preferred region
   - **Branch**: `main` (or your branch)
   - **Dockerfile Path**: `./server/Dockerfile`
   - **Docker Context**: `.`
4. Add Environment Variables (see below)
5. Click **Create Web Service**

## Environment Variables

Add these environment variables to your web service:

### Required Variables

- `ENV` = `production`
- `DATABASE_URL` = (Use "Connect" from your PostgreSQL service to get the internal connection string)
- `REDIS_URL` = (Use "Connect" from your Redis service to get the internal connection string)
- `CORS_ORIGINS` = Your frontend URL (e.g., `https://your-frontend.vercel.app,https://www.yourdomain.com`)
- `ORCHESTRATOR` = `langgraph`

### Optional Variables

- `OPENAI_API_KEY` = Your OpenAI API key
- `ANTHROPIC_API_KEY` = Your Anthropic API key
- `LOCAL_LLAMA_ENDPOINT` = URL to local LLM endpoint
- `LANGSMITH_API_KEY` = LangSmith API key for tracing
- `LANGSMITH_TRACING` = `true` (if using LangSmith)
- `POWER_AUTOMATE_WEBHOOK_URL` = Power Automate webhook URL for email notifications

### Using Internal Connections

Render provides internal connection strings for services in the same region. Use these for better performance:

**PostgreSQL Internal URL Format:**
```
postgresql://user:password@hostname:5432/database
```

**Redis Internal URL Format:**
```
redis://red-xxxxx:6379
```

You can find these in the "Connect" section of each service.

## Database Setup

After deployment, you need to initialize the database:

### Option 1: Run initialization script

1. Go to your web service in Render Dashboard
2. Open the **Shell** tab
3. Run:
   ```bash
   python -c "from app.init_db import init; init()"
   ```

### Option 2: Connect and run SQL manually

If you need to set up the database schema manually, connect to your PostgreSQL database and run the necessary migrations.

## pgvector Extension

The application uses pgvector for embeddings. To enable it:

1. Connect to your PostgreSQL database
2. Run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

Most Render PostgreSQL plans support this extension out of the box.

## Health Check

Your API includes a health check endpoint at `/api/health`. Render will use this to monitor your service.

Test it after deployment:
```bash
curl https://your-service.onrender.com/api/health
```

Expected response:
```json
{"status": "ok"}
```

## Connecting Frontend

Update your frontend's environment variable to point to your Render backend:

```
NEXT_PUBLIC_API_BASE=https://your-service.onrender.com
```

## Monitoring

- View logs in real-time from the Render dashboard
- Set up log streaming to external services if needed
- Monitor database and Redis usage from their respective dashboards

## Troubleshooting

### Database Connection Issues

- Verify `DATABASE_URL` is set correctly
- Check that the database is in the same region as your web service
- Ensure the database is running (check PostgreSQL dashboard)

### Redis Connection Issues

- Verify `REDIS_URL` is set correctly
- Check that Redis is in the same region as your web service
- Ensure Redis is running (check Redis dashboard)

### Deployment Failures

- Check the build logs in Render dashboard
- Verify Dockerfile is correctly configured
- Ensure all required dependencies are in `requirements.txt`

### Port Issues

The application automatically uses the `PORT` environment variable provided by Render (usually 10000). No manual configuration needed.

## Cost Optimization

### Free Tier Limits

- **Web Service (Free)**: 750 hours/month, sleeps after 15 min of inactivity
- **PostgreSQL (Free)**: 1GB storage, 97 connection limit
- **Redis (Free)**: 25MB storage

### Recommendations

1. Start with free tier for testing
2. Upgrade PostgreSQL to Starter ($7/month) for better performance and 2GB storage
3. Upgrade Redis to Starter ($10/month) for 256MB storage
4. Keep web service on free tier initially, upgrade if you need zero-downtime

## Scaling

As your application grows:

1. Upgrade to paid plans for more resources
2. Consider horizontal scaling for the web service
3. Enable auto-scaling based on CPU/memory usage
4. Use Redis for session caching to reduce database load

## Security Notes

1. Never commit API keys to the repository
2. Use Render's secret environment variables for sensitive data
3. Configure `CORS_ORIGINS` to only allow your frontend domain(s)
4. Regularly rotate database credentials
5. Enable SSL/TLS (Render provides this automatically)

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [Render PostgreSQL Guide](https://render.com/docs/databases)
- [Render Redis Guide](https://render.com/docs/redis)
- [Render Docker Deployments](https://render.com/docs/docker)
