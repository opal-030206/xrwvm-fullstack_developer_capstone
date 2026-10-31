# Deploying Cars Dealership to IBM Cloud Code Engine

These are the exact steps used for the capstone. You need an IBM Cloud account,
the IBM Cloud CLI, and Docker (or podman) installed.

## 0. Variables used below

```bash
export RG=cars-dealership-rg
export REGION=us-south
export REGISTRY=us.icr.io
export NAMESPACE=cars-dealership
export APP=cars-dealership
export SENTIMENT=cars-dealership-sentiment
```

## 1. Log in and prepare the registry

```bash
ibmcloud login --sso -r $REGION
ibmcloud target -g Default -r $REGION
ibmcloud plugin install container-registry -f
ibmcloud plugin install code-engine -f

ibmcloud cr namespace-add $NAMESPACE
ibmcloud cr login
```

## 2. Build and push the two images

The Django image compiles the React bundle inside the Docker build, so no
local Node build is required.

```bash
docker build -t $REGISTRY/$NAMESPACE/$APP:v1 .
docker build -f Dockerfile.sentiment \
  -t $REGISTRY/$NAMESPACE/$SENTIMENT:v1 .

docker push $REGISTRY/$NAMESPACE/$APP:v1
docker push $REGISTRY/$NAMESPACE/$SENTIMENT:v1
```

## 3. Deploy the sentiment microservice first

```bash
ibmcloud ce application create \
  --name $SENTIMENT \
  --image $REGISTRY/$NAMESPACE/$SENTIMENT:v1 \
  --port 8080 \
  --min-scale 0 --max-scale 2

ibmcloud ce application get --name $SENTIMENT --output url
# -> https://cars-dealership-sentiment.xxxx.us-south.codeengine.appdomain.cloud
```

## 4. Deploy the Django application

```bash
SENTIMENT_URL=$(ibmcloud ce application get --name $SENTIMENT --output url)

ibmcloud ce application create \
  --name $APP \
  --image $REGISTRY/$NAMESPACE/$APP:v1 \
  --port 8080 \
  --min-scale 0 --max-scale 3 \
  --env SENTIMENT_SERVICE_URL=$SENTIMENT_URL \
  --env CAR_DEALERSHIP_DEBUG=0 \
  --env DJANGO_SECRET_KEY="$(openssl rand -hex 32)"

ibmcloud ce application get --name $APP --output url
```

The image entry point runs `migrate` and `seed_data` before gunicorn starts, so
the first request already sees the 18 dealerships, the car catalogue and the
`root` / `root123` superuser.

> SQLite lives inside the container. On Code Engine that means every cold start
> re-seeds a fresh database, which is fine for the capstone demo. For durable
> data, point `DATABASES` at a managed PostgreSQL instance and use
> `ibmcloud ce application update --env DATABASE_URL=...`.

## 5. Verify the deployment

```bash
APP_URL=$(ibmcloud ce application get --name $APP --output url)

curl -s "$APP_URL/djangoapp/get_dealers" | head -c 200
curl -s "$APP_URL/djangoapp/get_dealers/Kansas" | head -c 200
curl -s -X POST "$APP_URL/djangoapp/analyze_review" \
  -H 'Content-Type: application/json' -d '{"text":"Fantastic services"}'
```

## 6. Capture the deployed screenshots (Tasks 25-28)

With Chrome installed, the same capture helper used locally works against the
public URL and keeps the address bar in frame:

```bash
node tools/shoot-deployed.mjs "$APP_URL"
```

This writes `screenshots/deployed_landingpage.png`,
`deployed_loggedin.png`, `deployed_dealer_detail.png` and
`deployed_add_review.png`.

Finally record the URL for Task 24:

```bash
echo "$APP_URL" > submission/deploymentURL
```

## 7. Redeploying after changes

```bash
docker build -t $REGISTRY/$NAMESPACE/$APP:v2 .
docker push $REGISTRY/$NAMESPACE/$APP:v2
ibmcloud ce application update --name $APP \
  --image $REGISTRY/$NAMESPACE/$APP:v2
```

## Clean up

```bash
ibmcloud ce application delete --name $APP --force
ibmcloud ce application delete --name $SENTIMENT --force
ibmcloud cr namespace-delete $NAMESPACE -f
```
