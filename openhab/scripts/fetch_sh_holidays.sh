#!/bin/bash
# fetch_sh_holidays.sh <validFrom> <validTo>
# Fetch Schleswig-Holstein school holidays (openholidaysapi.org). Cache on success,
# fall back to cache on failure so an API outage cannot break the wake logic.
CACHE=/var/lib/openhab2/sh_holidays_cache.json
FROM="$1"; TO="$2"
URL="https://openholidaysapi.org/SchoolHolidays?countryIsoCode=DE&subdivisionCode=DE-SH&languageIsoCode=DE&validFrom=${FROM}&validTo=${TO}"
OUT=$(curl -s --max-time 25 -H "accept: application/json" "$URL")
if [ -n "$OUT" ] && printf %s "$OUT" | head -c1 | grep -q "\["; then
  printf %s "$OUT" > "$CACHE"
  printf %s "$OUT"
else
  cat "$CACHE" 2>/dev/null
fi
