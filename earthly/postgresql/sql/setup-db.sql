-- Initialize the Project Catalyst Event Database.
-- sqlfluff:dialect:postgres

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
\echo -> dbSuperUser ............ = :dbSuperUser

-- Cleanup if we already ran this before.
--DROP OWNED BY IF EXISTS :"dbUser"; -- noqa: PRS
DROP DATABASE IF EXISTS :"dbName"; -- noqa: PRS
DROP USER IF EXISTS :"dbUser"; -- noqa: PRS

-- Create the test user we will use with the local dev database.
CREATE USER :"dbUser" WITH PASSWORD :'dbUserPw'; -- noqa: PRS

-- Privileges for this user/role.
ALTER DEFAULT PRIVILEGES GRANT EXECUTE ON FUNCTIONS TO public;

-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT EXECUTE ON FUNCTIONS
-- TO :"dbUser"; -- noqa: PRS

-- Create the database.
CREATE DATABASE :"dbName" WITH OWNER :"dbUser"; -- noqa: PRS

-- This is necessary for RDS to work.
GRANT :"dbUser" TO :"dbSuperUser";

COMMENT ON DATABASE :"dbName" IS :'dbDescription'; -- noqa: PRS
