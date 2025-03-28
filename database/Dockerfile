FROM mcr.microsoft.com/mssql/server:2019-latest

# Set environment variables required by SQL Server
ENV ACCEPT_EULA=Y
ENV SA_PASSWORD=Scam@1992
ENV MSSQL_PID=Express

# Switch to root user for the installation steps
USER root

# Remove any existing apt lists and recreate them with proper permissions
RUN rm -rf /var/lib/apt/lists && mkdir -p /var/lib/apt/lists/partial && chmod -R 755 /var/lib/apt/lists

# Install mssql-tools and its dependencies
RUN apt-get update && apt-get install -y \
    curl \
    apt-transport-https \
    gnupg \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 mssql-tools \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the initialization and entrypoint scripts
COPY init.sql /init.sql
COPY entrypoint.sh /entrypoint.sh

# Use the custom entrypoint to start SQL Server and run init.sql
ENTRYPOINT ["/entrypoint.sh"]
