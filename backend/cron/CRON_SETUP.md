# Cron Setup Guide for MongoDB Atlas

Your scripts are already configured to use MongoDB Atlas. This guide will help you set up automated cron jobs.

## Current Configuration

Your `.env` file contains:
```
MONGO_URI="mongodb+srv://f20200647p_db_user:SavemyLife123@m0.nn1voal.mongodb.net/?appName=M0"
```

All Python scripts use this connection string with `certifi` for SSL/TLS verification.

## Setup Instructions

### For Linux/Mac (Production Server)

1. **Make the script executable:**
```bash
chmod +x backend/cron/run_daily_pipeline.sh
```

2. **Test the script manually:**
```bash
cd /path/to/your/project
./backend/cron/run_daily_pipeline.sh
```

3. **Set up crontab:**
```bash
crontab -e
```

4. **Add one of these cron schedules:**

Run daily at 8 PM IST (2:30 PM UTC):
```
30 14 * * * /path/to/your/project/backend/cron/run_daily_pipeline.sh
```

Run daily at 11 PM IST (5:30 PM UTC):
```
30 17 * * * /path/to/your/project/backend/cron/run_daily_pipeline.sh
```

Run every weekday at 9 PM IST:
```
30 15 * * 1-5 /path/to/your/project/backend/cron/run_daily_pipeline.sh
```

5. **Verify cron is running:**
```bash
crontab -l
```

6. **Check logs:**
```bash
tail -f backend/logs/daily_pipeline_*.log
```

### For Windows (Task Scheduler)

1. **Open Task Scheduler** (taskschd.msc)

2. **Create Basic Task:**
   - Name: "MF Screener Daily Pipeline"
   - Trigger: Daily at your preferred time
   - Action: Start a program
   - Program: `C:\Windows\System32\cmd.exe`
   - Arguments: `/c "C:\path\to\project\backend\cron\run_daily_pipeline.bat"`
   - Start in: `C:\path\to\project\backend`

3. **Advanced Settings:**
   - Run whether user is logged on or not
   - Run with highest privileges
   - Configure for: Windows 10

4. **Test the task:**
   - Right-click the task → Run
   - Check logs in `backend\logs\`

### For Cloud Deployment (Recommended)

#### Option 1: GitHub Actions (Free)

Create `.github/workflows/daily-pipeline.yml`:
```yaml
name: Daily Data Pipeline

on:
  schedule:
    - cron: '30 14 * * *'  # 8 PM IST
  workflow_dispatch:  # Manual trigger

jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run pipeline
        env:
          MONGO_URI: ${{ secrets.MONGO_URI }}
          DB_NAME: mfscreener
        run: |
          cd backend
          python cron/daily_pipeline.py
```

Add `MONGO_URI` to GitHub Secrets:
- Go to repo Settings → Secrets and variables → Actions
- Add new secret: `MONGO_URI` with your connection string

#### Option 2: Render Cron Jobs

1. Create `render.yaml`:
```yaml
services:
  - type: cron
    name: daily-pipeline
    env: python
    schedule: "30 14 * * *"
    buildCommand: "pip install -r backend/requirements.txt"
    startCommand: "python backend/cron/daily_pipeline.py"
    envVars:
      - key: MONGO_URI
        sync: false
      - key: DB_NAME
        value: mfscreener
```

2. Deploy to Render and set `MONGO_URI` in environment variables

#### Option 3: Railway Cron

1. Deploy your backend to Railway
2. Add cron service in `railway.toml`:
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python backend/cron/daily_pipeline.py"
cronSchedule = "30 14 * * *"
```

## Troubleshooting

### Issue: "No module named 'pymongo'"
**Solution:** Install dependencies in the cron environment
```bash
pip3 install -r backend/requirements.txt
```

### Issue: "MONGO_URI not found"
**Solution:** Ensure .env file is in the project root and readable
```bash
ls -la .env
cat .env | grep MONGO_URI
```

### Issue: "Connection timeout"
**Solution:** Check MongoDB Atlas network access
- Go to MongoDB Atlas → Network Access
- Add IP address: `0.0.0.0/0` (allow from anywhere) or your server IP

### Issue: "Authentication failed"
**Solution:** Verify credentials in .env file match MongoDB Atlas user

### Issue: Cron runs but no data updates
**Solution:** Check logs for errors
```bash
tail -100 backend/logs/daily_pipeline_*.log
```

## Manual Testing

Test individual scripts:
```bash
cd backend

# Test benchmark ingestion
python data_ingestion/benchmarks/store_nav_daily_benchmark_nse.py

# Test NAV ingestion
python data_ingestion/amfi/store_nav.py

# Test scoring
python scoring/large_cap_score_phase3a.py
```

## Monitoring

Check if data is being updated:
```python
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["mfscreener"]

# Check latest NAV date
latest = db.nav_history.find_one(sort=[("date", -1)])
print(f"Latest NAV: {latest['date']}")

# Check latest benchmark
latest_bench = db.benchmark_nav.find_one(sort=[("date", -1)])
print(f"Latest Benchmark: {latest_bench['date']}")
```

## Logs Location

- Linux/Mac: `backend/logs/daily_pipeline_YYYYMMDD_HHMMSS.log`
- Windows: `backend\logs\daily_pipeline_YYYYMMDD_HHMMSS.log`
- Logs older than 30 days are automatically deleted

## Support

If issues persist:
1. Check MongoDB Atlas connection from your server
2. Verify all Python dependencies are installed
3. Review log files for specific errors
4. Ensure .env file has correct credentials
