#!/usr/bin/env bash
# Upgrade the four Oracle support containers to their :latest images, one at a time.
# Safe against data loss: every writable path is a host bind mount that survives
# recreation (verified) — nothing durable lives in the container layer.
#   hh-dagu   /mnt/data/docker-volumes/dagu, /mnt/data/backups/postgres
#   homepage  /mnt/data/home-dashboard/homepage-config
#   hh-9router /mnt/data/9router:/app/data
#   hh-pgweb  stateless; config in /mnt/data/secrets/pgweb.env, DB is untouched hh-postgres
# Never touches hh-postgres/hh-app/hh-cloudflared/olivetin; no down/prune.

ssh hh bash -s <<'REMOTE'
chmod 600 /mnt/data/secrets/pgweb.env

# Pull + recreate one service at a time; deploy-jobs.sh injects Bitwarden env for Dagu.
/mnt/data/compose/deploy-jobs.sh
cd /mnt/data/home-dashboard && docker compose -f compose.yml pull homepage && docker compose -f compose.yml up -d --no-deps homepage
cd /mnt/data/compose && docker compose -f 9router.compose.yml pull hh-9router && docker compose -f 9router.compose.yml up -d --no-deps hh-9router
docker compose -f pgweb.compose.yml pull pgweb && docker compose -f pgweb.compose.yml up -d --no-deps pgweb

docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}' \
  --filter name=hh-dagu --filter name=home-dashboard-homepage --filter name=hh-9router --filter name=hh-pgweb
REMOTE
