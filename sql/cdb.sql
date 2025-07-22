psql -U postgres
CREATE DATABASE notifications;
CREATE USER notifications_user WITH PASSWORD '1111n';
GRANT ALL PRIVILEGES ON DATABASE notifications TO notifications_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO notifications_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO notifications_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO notifications_user;
