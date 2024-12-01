-- A srcript that ranks origins of bands

SELECT origin, SUM(fans) AS nb_fans
FROM metal_bands
GROUP by origin
ORDER BY nb_fans DESC;
