#!/bin/sh
set -eu

# App Service / container env var expected:
#   API_BASE_URL=https://app-weather-analytics-api-wus2.azurewebsites.net/api/weather
: "${API_BASE_URL:=}"

cat > /usr/share/nginx/html/env.js <<EOF
window.__ENV__ = window.__ENV__ || {};
window.__ENV__.API_BASE_URL = "${API_BASE_URL}";
EOF
