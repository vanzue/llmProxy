# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container (for documentation purposes)
EXPOSE 5000

# Run the application with gunicorn, dynamically binding to PORT environment variable
CMD ["gunicorn", "--bind", "0.0.0.0:" + os.environ.get('PORT', '5000'), "--timeout", "300", "app:app"]
