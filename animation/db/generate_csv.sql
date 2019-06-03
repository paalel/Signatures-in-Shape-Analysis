.headers on
.mode csv

.output similarity.csv
SELECT animation_id1, animation_id2, signature_distance
FROM similarity 
ORDER BY animation_id1;

.output names.csv
SELECT animation_id, 
description || ' (' || substr(file_name, -4, -100) || ')'
FROM animation 
WHERE animation_id IN (
	SELECT distinct(animation_id1) FROM similarity 
)
ORDER BY animation_id;
.quit
