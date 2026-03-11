## AB Analytics API with Planout

A/B testing group assignment and experiment data collection API. When a client sends user information, the API assigns users to experiments matching conditions (platform, country, version, etc.) and determines variations based on Planout. Experiment participation/callback events are sent to Kafka.

**API Flow:** `POST /api/abtest/segment` → API Key validation → User info lookup from Redis/MySQL → Country correction via GeoIP → Experiment condition matching → Group assignment via Planout → Kafka event publishing → Response

**Tech Stack**
- **Language:** Python 3.11
- **Framework:** FastAPI, Uvicorn, Gunicorn
- **DB:** MySQL (aiomysql), SQLAlchemy (async)
- **Infrastructure:** Redis (cache), Kafka (event streaming)
- **Others:** Pydantic, GeoIP2(MaxMind), pandas, Planout

---

### Local Test Environment Setup
#### 1. **Using Docker**
##### 1-1. **Build Docker Image**
   ```bash
   docker buildx build --load -f Dockerfile.dev --platform=linux/amd64 -t ab-analytics-api.local .
   ```
##### 1-2. **Run Docker Container**
   ```bash
   docker run --name ab-analytics-api.container -p 8001:8001 -v $(pwd)/app:/code/app ab-analytics-api.local
   ```
#### 2. **Using Python Virtual Environment**
   ```bash
   pkill -f uvicorn
   PROJECT_LOCAL_PATH=`pwd -P`
   source ${PROJECT_LOCAL_PATH}/venv/bin/activate

   echo "check pip packages.."
   pip3 install -r ${PROJECT_LOCAL_PATH}/requirements.txt
   pip3 freeze > ./requirements.txt
   cp ./.env.dev ./.env
   ${PROJECT_LOCAL_PATH}/venv/bin/uvicorn app.main:app --reload --host=0.0.0.0 --port 8001
   ```