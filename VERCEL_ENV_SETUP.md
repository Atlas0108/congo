# Setting Up Environment Variables in Vercel

## Step 1: Add DATABASE_URL

1. Go to your Vercel project dashboard: https://vercel.com/dashboard
2. Select your project (congo-app)
3. Go to **Settings** → **Environment Variables**
4. Click **Add New**
5. Add the following:

   **Variable Name:** `DATABASE_URL`
   
   **Value:** 
   ```
   postgresql://neondb_owner:npg_79qFZAtaUpQg@ep-lingering-sunset-ai9zz9jp-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```
   
   **Environment:** Select all (Production, Preview, Development)

6. Click **Save**

## Step 2: Add SECRET_KEY (Optional but Recommended)

Add a secret key for Flask sessions:

**Variable Name:** `SECRET_KEY`

**Value:** (Generate a random string, e.g., use `python -c "import secrets; print(secrets.token_hex(32))"`)

**Environment:** Select all

## Step 3: Redeploy

After adding environment variables, you need to redeploy:

1. Go to **Deployments** tab
2. Click the **⋯** menu on the latest deployment
3. Click **Redeploy**
4. Or use CLI: `vercel --prod`

## Important Notes

- **Pooled Connection**: The connection string uses `-pooler` which is recommended for serverless/Vercel
- **SSL Required**: The `?sslmode=require` parameter is included for secure connections
- **Environment Scope**: Make sure to add the variables to all environments (Production, Preview, Development) so they work everywhere

## Verify It's Working

After redeploying, check:
1. Go to **Deployments** → Latest deployment → **Logs**
2. Look for successful database connection messages
3. Visit your app URL and check if it loads without 500 errors


