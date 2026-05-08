-- Remove Irisgatan Garden zone and its associated data
-- Run: docker-compose exec -T postgres psql -U olive_user -d olive_monitoring < backend/scripts/migrate_remove_garden_zone.sql

DELETE FROM health_indices WHERE zone_id IN (SELECT id FROM field_zones WHERE name = 'Irisgatan Garden');
DELETE FROM alerts WHERE zone_id IN (SELECT id FROM field_zones WHERE name = 'Irisgatan Garden');
DELETE FROM baseline_statistics WHERE zone_id IN (SELECT id FROM field_zones WHERE name = 'Irisgatan Garden');
DELETE FROM field_zones WHERE name = 'Irisgatan Garden';
