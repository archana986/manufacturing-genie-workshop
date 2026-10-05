CREATE OR REPLACE FUNCTION ${catalog}.${schema}.mask_operator_name(value STRING)
RETURNS STRING
RETURN CASE WHEN is_account_group_member('apex_pii_readers') THEN value ELSE 'REDACTED' END;

ALTER TABLE ${catalog}.${schema}.operators
ALTER COLUMN first_name SET MASK ${catalog}.${schema}.mask_operator_name;

ALTER TABLE ${catalog}.${schema}.operators
ALTER COLUMN last_name SET MASK ${catalog}.${schema}.mask_operator_name;
