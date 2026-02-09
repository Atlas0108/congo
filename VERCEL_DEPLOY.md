# Deploying to Vercel

## Prerequisites

1. **Vercel account**: Sign up at https://vercel.com (free)
2. **Vercel CLI**: Install it:
   ```bash
   npm install -g vercel
   ```

## Setup Steps

### 1. Install Vercel CLI (if not already installed)
```bash
npm install -g vercel
```

### 2. Login to Vercel
```bash
vercel login
```

### 3. Set Environment Variables

You'll need to set your database URL and other environment variables in Vercel:

```bash
vercel env add DATABASE_URL
# Paste your database connection string when prompted

vercel env add SECRET_KEY
# Enter a secret key for Flask sessions
```

Or set them in the Vercel dashboard:
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add your variables

**Required Environment Variables:**
- `DATABASE_URL` - Your PostgreSQL connection string (you can use Vercel Postgres or any PostgreSQL database)
- `SECRET_KEY` - A secret key for Flask sessions

### 4. Deploy

**First deployment:**
```bash
vercel
```

Follow the prompts:
- Set up and deploy? **Yes**
- Which scope? (your account)
- Link to existing project? **No**
- Project name? (press enter for default)
- Directory? (press enter for current directory)

**Subsequent deployments:**
```bash
vercel --prod
```

### 5. Access Your App

After deployment, Vercel will give you a URL like:
```
https://your-project-name.vercel.app
```

## Important Notes

### Database Setup

Vercel doesn't provide a database by default. You have a few options:

1. **Vercel Postgres** (Recommended for Vercel):
   - Add Vercel Postgres in your project dashboard
   - It will automatically set `POSTGRES_URL` environment variable
   - Update your code to use `POSTGRES_URL` if needed

2. **External PostgreSQL**:
   - Use services like:
     - **Neon** (free tier): https://neon.tech
     - **Supabase** (free tier): https://supabase.com
     - **Railway** (free tier): https://railway.app
   - Get the connection string and set it as `DATABASE_URL`

3. **SQLite** (for simple testing):
   - Not recommended for production, but works for quick previews
   - Update `DATABASE_URL` to use SQLite

### Limitations

- **Cold starts**: Serverless functions have cold start delays (usually 1-2 seconds)
- **Function timeout**: Free tier has 10-second timeout, Pro has 60 seconds
- **Database connections**: Make sure your database allows connections from Vercel's IPs
- **File uploads**: Limited to 4.5MB on free tier

### Updating Your App

Every time you push to your connected Git branch, Vercel will automatically deploy. Or deploy manually:

```bash
vercel --prod
```

## Troubleshooting

### Database Connection Issues

If you see database connection errors:
1. Check your `DATABASE_URL` is set correctly
2. Ensure your database allows external connections
3. For Vercel Postgres, use the `POSTGRES_URL` variable

### Static Files Not Loading

Static files should work automatically. If they don't:
- Check that files are in `frontend/static/`
- Ensure `vercel.json` routes are correct

### Function Timeout

If requests timeout:
- Check database query performance
- Consider upgrading to Pro plan for longer timeouts
- Optimize slow operations

## Quick Start Commands

```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel

# Deploy to production
vercel --prod

# View logs
vercel logs
```


