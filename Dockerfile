# Use the official PostgreSQL image from the Docker hub
FROM postgres:13

# Set environment variables
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=password
ENV PGDATA=/var/lib/postgresql/data/pgdata

# Expose the port PostgreSQL will use
EXPOSE 5432

# Volume for the database data
VOLUME /var/lib/postgresql/data
