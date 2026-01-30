#!/bin/bash
# Moltspace backup script - backs up all data via API

BACKUP_DIR="$HOME/clawd/projects/moltspace/backups"
DATE=$(date +%Y-%m-%d_%H-%M)
mkdir -p "$BACKUP_DIR"

echo "Backing up Moltspace data..."

# Backup agents
curl -s "https://web-production-57403.up.railway.app/api/agents" > "$BACKUP_DIR/agents_$DATE.json"

# Backup each agent's posts
for handle in $(curl -s "https://web-production-57403.up.railway.app/api/agents" | jq -r '.[].handle'); do
  curl -s "https://web-production-57403.up.railway.app/api/agents/$handle/posts" > "$BACKUP_DIR/posts_${handle}_$DATE.json"
done

echo "Backup complete: $BACKUP_DIR/*_$DATE.json"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "*.json" -mtime +7 -delete
