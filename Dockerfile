# Use the official Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY ./my-python-project/ /app

# Install dependencies (if any)
RUN pip install --no-cache-dir python-dotenv

# Set environment variables (optional, or use a .env file)
ENV TEST_FILE_NAME=test_file

# Run the Python script
CMD ["python", "src/test.py"]