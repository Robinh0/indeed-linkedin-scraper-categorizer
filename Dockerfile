# Use the official AWS Lambda Python 3.12 image
FROM public.ecr.aws/lambda/python:3.11

# Set the working directory to Lambda's task root
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy dependencies first for caching
COPY requirements.txt ./

# Install dependencies
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of the application code to ${LAMBDA_TASK_ROOT}
COPY . .

# Set the Lambda-compatible handler
CMD ["main.handler"]
