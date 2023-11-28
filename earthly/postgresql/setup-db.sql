-- Initialize the Project Catalyst Event Database.

-- cspell: words psql

-- This script requires a number of variables to be set.
-- They will default if not set externally.
-- These variables can be set on the "psql" command line.
-- Passwords may optionally be set by ENV Vars.
-- This script requires "psql" is run inside a POSIX compliant shell.

-- VARIABLES:

-- DISPLAY ALL VARIABLES
\echo VARIABLES:
\echo -> dbName ................. = :dbName
\echo -> dbDescription .......... = :dbDescription
\echo -> dbUser ................. = :dbUser
\echo -> dbUserPw ............... = xxxx

-- Cleanup if we already ran this before.
DROP DATABASE IF EXISTS :"dbName"; -- noqa: PRS
DROP USER IF EXISTS :"dbUser"; -- noqa: PRS

-- Create the test user we will use with the local dev database.
CREATE USER :"dbUser" WITH PASSWORD :'dbUserPw'; -- noqa: PRS

-- Privileges for this user/role.
ALTER DEFAULT privileges REVOKE EXECUTE ON functions FROM public;

ALTER DEFAULT privileges IN SCHEMA public REVOKE EXECUTE ON functions FROM :"dbUser"; -- noqa: PRS

-- Create the database.
CREATE DATABASE :"dbName" WITH OWNER :"dbUser"; -- noqa: PRS

COMMENT ON DATABASE :"dbName" IS :'dbDescription'; -- noqa: PRS
