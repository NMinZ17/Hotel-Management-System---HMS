-- ============================================================================
-- SCRIPT: database/scripts/init_databases.sql
-- Mục đích: Khởi tạo 3 database độc lập (dev, test, bench) và user riêng biệt
-- Cách chạy: psql -U postgres -v ON_ERROR_STOP=1 -f database/scripts/init_databases.sql
-- ============================================================================

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'hms_dev_user') THEN
        CREATE USER hms_dev_user WITH PASSWORD 'dev_secret_change_me';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'hms_test_user') THEN
        CREATE USER hms_test_user WITH PASSWORD 'test_secret_change_me';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'hms_bench_user') THEN
        CREATE USER hms_bench_user WITH PASSWORD 'bench_secret_change_me';
    END IF;
END $$;

-- Lưu ý: CREATE DATABASE không thể chạy bên trong khối DO/transaction
DROP DATABASE IF EXISTS hms_dev;
DROP DATABASE IF EXISTS hms_test;
DROP DATABASE IF EXISTS hms_bench;

CREATE DATABASE hms_dev   OWNER hms_dev_user   ENCODING 'UTF8' TEMPLATE template0;
CREATE DATABASE hms_test  OWNER hms_test_user  ENCODING 'UTF8' TEMPLATE template0;
CREATE DATABASE hms_bench OWNER hms_bench_user ENCODING 'UTF8' TEMPLATE template0;

GRANT ALL PRIVILEGES ON DATABASE hms_dev   TO hms_dev_user;
GRANT ALL PRIVILEGES ON DATABASE hms_test  TO hms_test_user;
GRANT ALL PRIVILEGES ON DATABASE hms_bench TO hms_bench_user;