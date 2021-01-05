# Overhave

## Preparation

Before service usage you should create database with name from
environment variable `OVERHAVE_DB_URL`. By default, the database name
is `overhave` with `postgres` owner.
Then, you should create tables.

1. Start postgres database.
2. Create tables or use migrations.
3. Start admin with `overhave admin` or use custom script.

`OverhaveContext` could be defined and used before admin application
startup. All you need - is setup context to `OverhaveCore` instance
with `set_context` def.