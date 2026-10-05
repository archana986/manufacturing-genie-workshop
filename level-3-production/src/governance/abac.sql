-- Apply ABAC tags in your catalog. Example only. Replace group names.
ALTER TABLE ${catalog}.${schema}.operators SET TAGS ('pii' = 'name');
