FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install any additional tools you might need (optional)
RUN apt-get update && apt-get install -y vim

# Default command to keep the container running
CMD ["tail", "-f", "/dev/null"]