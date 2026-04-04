-- Fluxora database initialization
-- This runs once when the container is first created

SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- Ensure the database exists
CREATE DATABASE IF NOT EXISTS `fluxoradb`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE `fluxoradb`;

-- Revoke all privileges from root on non-local hosts
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');

-- Remove anonymous users
DELETE FROM mysql.user WHERE User='';

-- Remove test database
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';

FLUSH PRIVILEGES;
