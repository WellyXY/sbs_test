# Use a slim Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the backend directory
COPY backend/ /app/

# Set the port
EXPOSE 8080

# Run the minimal server directly
CMD ["python", "-u", "/app/main_very_simple.py"] 