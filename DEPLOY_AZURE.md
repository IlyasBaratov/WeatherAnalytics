# Deploy to Azure (ACR + App Service for Containers) — single image

This repo deploys **UI + API together as a single container image**.

- One image (built from `./Dockerfile`) serves:
  - UI (static files): `/` (and `/index.html`, `/ski_index.html`)
  - API: `/api/weather/*`, `/api/ski/*`
  - Swagger docs: `/api/docs`

> This workflow uses `az acr build` so you do **not** need `docker build/tag/push` locally.

---

## 0) Prerequisites

- Azure CLI installed (`az --version`)
- You’re logged in: `az login`
- Optional: choose the right subscription: `az account set -s "<subscriptionIdOrName>"`

Providers (run once per subscription):

```powershell
az provider register -n Microsoft.ContainerRegistry
az provider register -n Microsoft.App
az provider register -n Microsoft.OperationalInsights
az provider register -n Microsoft.DBforPostgreSQL
```

---

## 1) Choose names

Pick your own values:

```powershell
$RG = "weather-rg"
$LOCATION = "westus2"
$ACR = "<uniqueAcrName>"      # must be globally unique
$TAG = "v1"

$WEBAPP = "app-weather-analytics"   # Azure App Service name
$IMAGE_REPO = "weather-api"         # ACR repository name (single image)

$PG_SERVER = "<uniquePgServerName>"  # must be globally unique
$PG_DB = "weather_db"
$PG_USER = "weather"
$PG_PASSWORD = "<choose-a-strong-password>"
```

---

## 2) Create Resource Group + ACR

```powershell
az group create -n $RG -l $LOCATION

az acr create -g $RG -n $ACR --sku Basic
```

---

## 3) Build + push BOTH images to ACR (cloud build)

From the repo root (this folder), build/push the **single** image:

```powershell
az acr build -r $ACR -t $IMAGE_REPO:$TAG -f Dockerfile .
```

Verify it exists:

```powershell
az acr repository list -n $ACR -o table
az acr repository show-tags -n $ACR --repository $IMAGE_REPO -o table
```

---

## 4) Create PostgreSQL (Azure Database for PostgreSQL Flexible Server)

The app supports SQLite locally, but for Azure you’ll typically use Postgres.

Create a Postgres server + DB:

```powershell
az postgres flexible-server create `
  -g $RG -n $PG_SERVER -l $LOCATION `
  --tier Burstable --sku-name Standard_B1ms `
  --storage-size 32 `
  --admin-user $PG_USER --admin-password $PG_PASSWORD

az postgres flexible-server db create -g $RG -s $PG_SERVER -d $PG_DB
```

Allow Azure services to reach it (simplest starting point):

```powershell
az postgres flexible-server firewall-rule create -g $RG -s $PG_SERVER -n AllowAzure `
  --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0
```

Build the SQLAlchemy connection string:

```powershell
$PG_HOST = (az postgres flexible-server show -g $RG -n $PG_SERVER --query fullyQualifiedDomainName -o tsv)
$DATABASE_URL = "postgresql+psycopg2://$PG_USER`:$PG_PASSWORD@$PG_HOST:5432/$PG_DB?sslmode=require"
```

---

## 5) Create the App Service (Linux) (if needed)

If you already created the web app, skip this section.

```powershell
$PLAN = "$WEBAPP-plan"

az appservice plan create -g $RG -n $PLAN --is-linux --sku B1

az webapp create -g $RG -n $WEBAPP -p $PLAN --deployment-container-image-name "nginx"
```

---

## 6) Configure the App Service to run the image (Managed Identity pull)

Assign a managed identity and grant it `AcrPull` on the registry:

```powershell
$MI_PRINCIPAL_ID = (az webapp identity assign -g $RG -n $WEBAPP --query principalId -o tsv)
$ACR_ID = (az acr show -g $RG -n $ACR --query id -o tsv)

az role assignment create --assignee-object-id $MI_PRINCIPAL_ID --assignee-principal-type ServicePrincipal --role AcrPull --scope $ACR_ID
```

Point your web app at the image:

```powershell
$ACR_LOGIN_SERVER = (az acr show -g $RG -n $ACR --query loginServer -o tsv)
$IMAGE = "$ACR_LOGIN_SERVER/$IMAGE_REPO:$TAG"

az webapp config container set -g $RG -n $WEBAPP \
  --docker-custom-image-name $IMAGE \
  --docker-registry-server-url ("https://{0}" -f $ACR_LOGIN_SERVER)

# Tell App Service to use managed identity when pulling from ACR
az webapp config appsettings set -g $RG -n $WEBAPP --settings acrUseManagedIdentityCreds=true

# Container listens on 8000
az webapp config appsettings set -g $RG -n $WEBAPP --settings WEBSITES_PORT=8000

az webapp restart -g $RG -n $WEBAPP
```

Test:

- UI: `https://<webapp-host>/`
- Ski UI: `https://<webapp-host>/ski_index.html`
- API health: `https://<webapp-host>/api/health`
- Swagger: `https://<webapp-host>/api/docs`

---

## Notes / Common issues

- If the API can’t connect to Postgres, verify `DATABASE_URL` and that Postgres firewall allows Azure services.
- If the UI still calls an old API host, verify your deployment is serving `/env.js` and that the browser loads it (Network tab).
- The `docker-compose.yml` `version:` key is obsolete in new Docker Compose; it can be removed without changing behavior.
