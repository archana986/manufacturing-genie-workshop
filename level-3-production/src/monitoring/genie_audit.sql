SELECT
  event_time,
  user_identity.email AS user_email,
  action_name,
  request_params['space_id'] AS space_id
FROM system.access.audit
WHERE service_name = 'aibiGenie'
  AND event_date >= date_sub(current_date(), 14)
ORDER BY event_time DESC
LIMIT 1000;
