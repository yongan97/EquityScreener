# Stock Screener GARP - Deployment Guide

This guide walks you through deploying the Stock Screener GARP as a web application with:
- **Supabase** (PostgreSQL database)
- **Vercel** (Next.js frontend)
- **GitHub Actions** (daily cron job)

## Architecture

```
+------------------+     +------------------+     +--------------------+
|  Vercel Frontend |<--->|    Supabase      |<----|  GitHub Actions    |
|  (Next.js)       |     |    (Postgres)    |     |  (Cron diario)     |
+------------------+     +------------------+     +--------------------+
                                                          |
                                                          v
                                                  +------------------+
                                                  |  Python Screener |
                                                  |  (stock-screener)|
                                                  +------------------+
```

## Cost: $0/month (Free Tiers)

| Service | Plan | Cost |
|---------|------|------|
| Vercel | Hobby | Free |
| Supabase | Free tier (500MB) | Free |
| GitHub Actions | Free tier | Free |
| FMP API | Free tier (250 req/day) | Free |

---

## Step 1: Get FMP API Key

1. Go to https://financialmodelingprep.com/developer
2. Click "Get my Free API key"
3. Create account with email
4. Copy the API key from dashboard
5. Save it securely for later

**Your FMP API Key**: `HJ6LvlkRLrEXMXvoJvXYtr7IJCetlWna`

---

## Step 2: Create Supabase Project

1. Go to https://supabase.com and create a free account
2. Click "New Project"
3. Fill in:
   - **Name**: `stock-screener-garp`
   - **Database Password**: Generate a strong password (save it!)
   - **Region**: Choose closest to you
4. Wait for project to be created (~2 minutes)

### Create Database Tables

1. In Supabase dashboard, go to **SQL Editor**
2. Click "New Query"
3. Copy and paste the contents of `stock-screener/database/schema.sql`
4. Click "Run" to execute

### Get API Keys

1. Go to **Settings > API**
2. Copy these values:
   - **Project URL**: `https://xxxx.supabase.co`
   - **anon public key**: For frontend (safe to expose)
   - **service_role key**: For backend (keep secret!)

---

## Step 3: Push Code to GitHub

If you don't have a repository yet:

```bash
cd C:/c/Equities

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Stock Screener GARP with web deployment"

# Create repo on GitHub and push
# (Replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/equities.git
git branch -M main
git push -u origin main
```

---

## Step 4: Configure GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings > Secrets and variables > Actions**
3. Add these secrets by clicking "New repository secret":

| Secret Name | Value |
|-------------|-------|
| `FMP_API_KEY` | `HJ6LvlkRLrEXMXvoJvXYtr7IJCetlWna` |
| `SUPABASE_URL` | `https://xxxx.supabase.co` |
| `SUPABASE_SERVICE_KEY` | Your service_role key |

---

## Step 5: Test GitHub Action Manually

1. Go to **Actions** tab in GitHub
2. Select "Daily Stock Screener" workflow
3. Click "Run workflow" > "Run workflow"
4. Wait for it to complete (~5-10 minutes)
5. Check Supabase dashboard to verify data was inserted

---

## Step 6: Deploy Frontend to Vercel

### Option A: Using Vercel CLI

```bash
cd stock-screener-web

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: stock-screener-web
# - Directory: ./
# - Override settings? No
```

### Option B: Using Vercel Dashboard

1. Go to https://vercel.com and login with GitHub
2. Click "Add New Project"
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `stock-screener-web`
5. Add environment variables:
   - `NEXT_PUBLIC_SUPABASE_URL`: Your Supabase project URL
   - `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Your anon public key
6. Click "Deploy"

---

## Step 7: Configure Supabase for Public Access

By default, Supabase tables are protected. For the frontend to read data:

1. Go to Supabase **SQL Editor**
2. Run:

```sql
-- Enable Row Level Security (optional but recommended)
ALTER TABLE screener_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE stocks ENABLE ROW LEVEL SECURITY;

-- Allow public read access
CREATE POLICY "Allow public read access to screener_runs"
ON screener_runs FOR SELECT
USING (true);

CREATE POLICY "Allow public read access to stocks"
ON stocks FOR SELECT
USING (true);

-- Grant access to views
GRANT SELECT ON latest_stocks TO anon;
GRANT SELECT ON latest_run TO anon;
GRANT SELECT ON stock_history TO anon;
```

---

## Verification Checklist

- [ ] FMP API key works (test locally: `python scripts/run_screener.py --limit 5`)
- [ ] Supabase tables created (check Tables in dashboard)
- [ ] GitHub Action runs successfully (check Actions tab)
- [ ] Data appears in Supabase after GitHub Action runs
- [ ] Frontend loads on Vercel URL
- [ ] Frontend shows stock data

---

## Troubleshooting

### GitHub Action fails

1. Check logs in GitHub Actions
2. Verify all secrets are set correctly
3. Test Supabase connection: `python scripts/run_screener_web.py test-connection`

### Frontend shows no data

1. Check browser console for errors
2. Verify environment variables in Vercel
3. Check Supabase RLS policies allow public access
4. Try running GitHub Action manually to populate data

### FMP API rate limit

Free tier allows 250 requests/day. The screener typically uses 200-300 per run.
If rate limited, wait 24 hours or upgrade FMP plan.

---

## Daily Schedule

The GitHub Action runs automatically at **6:00 AM EST (11:00 UTC)** Monday-Friday.

To change the schedule, edit `.github/workflows/daily-screener.yml`:

```yaml
on:
  schedule:
    - cron: '0 11 * * 1-5'  # 6:00 AM EST, Mon-Fri
```

Cron format: `minute hour day month weekday`

---

## Local Development

### Backend (Python)

```bash
cd stock-screener

# Create .env file
cp .env.example .env
# Edit .env with your API keys

# Install dependencies
pip install -r requirements.txt

# Run screener
python scripts/run_screener.py

# Or run and save to Supabase
python scripts/run_screener_web.py run
```

### Frontend (Next.js)

```bash
cd stock-screener-web

# Create .env.local file
cp .env.example .env.local
# Edit with your Supabase keys

# Install dependencies
npm install

# Run development server
npm run dev
# Open http://localhost:3000
```

---

## Updating

To update the screener or frontend:

1. Make changes locally
2. Commit and push to GitHub
3. Vercel auto-deploys frontend changes
4. GitHub Actions uses latest code on next run

---

## Support

For issues, check:
- GitHub Actions logs for backend errors
- Browser DevTools console for frontend errors
- Supabase logs for database errors
