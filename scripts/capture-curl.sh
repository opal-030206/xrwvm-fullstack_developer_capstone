#!/usr/bin/env bash
# Regenerates every cURL transcript in submission/ from a running local stack.
#
#   bash scripts/capture-curl.sh
#
# Requires: Django on :8000, Flask sentiment service on :5050.

set -uo pipefail
cd "$(dirname "$0")/.."

BASE="http://localhost:8000"
SENTIMENT="http://localhost:5050"
OUT="submission"
mkdir -p "$OUT"
rm -f cookies.txt

stamp() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

run() {
  local file="$1"
  local cmd="$2"
  {
    echo "# Cars Dealership capstone - cURL transcript"
    echo "# Captured: $(stamp)"
    echo "# Application: ${BASE}  (Flask sentiment service: ${SENTIMENT})"
    echo
    echo "\$ ${cmd}"
    echo
    eval "${cmd}"
    echo
  } > "${OUT}/${file}" 2>&1
  echo "wrote ${OUT}/${file}"
}

# --- Task 5: login -------------------------------------------------------
run loginuser \
  "curl -s -X POST ${BASE}/djangoapp/login -H 'Content-Type: application/json' -d '{\"userName\":\"root\",\"password\":\"root123\"}' -c cookies.txt -b cookies.txt"

# --- Task 6: logout (session cookie captured by the login above) ---------
run logoutuser \
  "curl -s -X POST ${BASE}/djangoapp/logout -b cookies.txt -c cookies.txt"

# --- Task 8: reviews for one dealer -------------------------------------
run getdealerreviews \
  "curl -s ${BASE}/djangoapp/reviews/dealer/1 | python -m json.tool"

# --- Task 9: every dealer -----------------------------------------------
run getalldealers \
  "curl -s ${BASE}/djangoapp/get_dealers | python -m json.tool"

# --- Task 10: a single dealer -------------------------------------------
run getdealerbyid \
  "curl -s ${BASE}/djangoapp/get_dealer/1 | python -m json.tool"

# --- Task 11: dealers in Kansas -----------------------------------------
run getdealersbyState \
  "curl -s ${BASE}/djangoapp/get_dealers/Kansas | python -m json.tool"

# --- Tasks 14 + 15: car makes and their models --------------------------
run getallcarmakes \
  "curl -s ${BASE}/djangoapp/get_cars | python -m json.tool"

# --- Task 16: sentiment for "Fantastic services" ------------------------
{
  echo "# Cars Dealership capstone - cURL transcript"
  echo "# Captured: $(stamp)"
  echo
  echo "# 1. The Flask sentiment analysis microservice, called directly:"
  echo "\$ curl -s -X POST ${SENTIMENT}/analyze -H 'Content-Type: application/json' -d '{\"text\":\"Fantastic services\"}'"
  echo
  curl -s -X POST "${SENTIMENT}/analyze" \
    -H 'Content-Type: application/json' \
    -d '{"text":"Fantastic services"}'
  echo
  echo
  echo "# 2. The same request through the Django proxy used by the web app:"
  echo "\$ curl -s -X POST ${BASE}/djangoapp/analyze_review -H 'Content-Type: application/json' -d '{\"text\":\"Fantastic services\"}'"
  echo
  curl -s -X POST "${BASE}/djangoapp/analyze_review" \
    -H 'Content-Type: application/json' \
    -d '{"text":"Fantastic services"}'
  echo
} > "${OUT}/analyzereview" 2>&1
echo "wrote ${OUT}/analyzereview"

rm -f cookies.txt
