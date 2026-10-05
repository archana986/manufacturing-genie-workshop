CREATE OR REPLACE FUNCTION ${catalog}.${schema}.plant_row_filter(plant_id STRING)
RETURNS BOOLEAN
RETURN is_account_group_member(concat('apex_plant_', plant_id))
    OR is_account_group_member('apex_all_plants');

ALTER TABLE ${catalog}.${schema}.production_events
SET ROW FILTER ${catalog}.${schema}.plant_row_filter ON (plant_id);
