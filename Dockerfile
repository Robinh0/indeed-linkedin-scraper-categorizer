# Use the official Python 3.10 image as the base
FROM python:3.10

# Set the working directory in the container to /app
WORKDIR /app

# Copy only requirements.txt first to leverage Docker caching for dependencies
COPY requirements.txt /app/

# Install Python dependencies early to cache them if they don't change
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Now copy the rest of your application code, this ensures code changes won't trigger a full rebuild
COPY . /app

# Command to run your Python application
CMD ["python", "extract.py"]
