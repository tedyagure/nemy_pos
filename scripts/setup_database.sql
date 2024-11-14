-- SQL Server Setup Script for Nemy POS
-- Run this script in SQL Server Management Studio (SSMS)

-- Create Database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'nemy_pos')
BEGIN
    CREATE DATABASE nemy_pos;
END
GO

USE nemy_pos;
GO

-- Create Login if it doesn't exist
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'nemy_user')
BEGIN
    CREATE LOGIN nemy_user WITH PASSWORD = 'your_strong_password';
END
GO

-- Create User and assign permissions
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'nemy_user')
BEGIN
    CREATE USER nemy_user FOR LOGIN nemy_user;
    ALTER ROLE db_owner ADD MEMBER nemy_user;
END
GO

-- Set database options
ALTER DATABASE nemy_pos SET READ_COMMITTED_SNAPSHOT ON;
GO

-- Enable full-text search
IF NOT EXISTS (SELECT * FROM sys.fulltext_catalogs WHERE name = 'nemy_pos_catalog')
BEGIN
    CREATE FULLTEXT CATALOG nemy_pos_catalog AS DEFAULT;
END
GO 