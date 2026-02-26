-- Migration: Add Irisgatan Garden zone (Malmö, Sweden)
-- Parsed from: olive-monitoring/Irisgatan 14.kml
-- Area: 577 m² (0.06 hectares)
-- Center: 55.573040°N, 12.995343°E
-- Date: 2026-02-26

INSERT INTO field_zones (name, description, geometry, area_hectares)
SELECT
    'Irisgatan Garden',
    'Home garden in Malmö, Sweden - satellite + IoT monitoring',
    '{"type": "Polygon", "coordinates": [[[12.99522906567615, 55.57308517016112], [12.99510789066416, 55.57283161389093], [12.9953762992967, 55.57278556531062], [12.99552235455895, 55.57309420072175], [12.99545199333202, 55.57310682333222], [12.99542447674449, 55.57307839961098], [12.99539570357765, 55.57308178858986], [12.995396853757, 55.57309732416563], [12.99532494937397, 55.57311420380201], [12.99531058487578, 55.57307638765403], [12.99522906567615, 55.57308517016112]]]}',
    0.06
WHERE NOT EXISTS (
    SELECT 1 FROM field_zones WHERE name = 'Irisgatan Garden'
);
