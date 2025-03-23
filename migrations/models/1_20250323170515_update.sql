-- upgrade --
ALTER TABLE "userdb" ALTER COLUMN "password" TYPE VARCHAR(100) USING "password"::VARCHAR(100);
-- downgrade --
ALTER TABLE "userdb" ALTER COLUMN "password" TYPE VARCHAR(50) USING "password"::VARCHAR(50);
