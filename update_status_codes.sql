-- 更新远程数据库中的状态码
-- 将状态8（已获取赛果）改为标准状态2（已完成）

-- TCZQ比赛
UPDATE tczq_match SET status = 2 WHERE status = 8;

-- BJDC比赛  
UPDATE bjdc_match SET status = 2 WHERE status = 8;

-- 验证更新结果
SELECT 'TCZQ' as table_name, status, COUNT(*) as count 
FROM tczq_match 
GROUP BY status
ORDER BY status;

SELECT 'BJDC' as table_name, status, COUNT(*) as count 
FROM bjdc_match 
GROUP BY status
ORDER BY status;
