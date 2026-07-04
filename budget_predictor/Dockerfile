# Use the official Python 3.11 image (slim for smaller size)
FROM python:3.11-slim

# Set up a new user named "user" with user ID 1000
# Hugging Face Spaces require running as a non-root user for security
RUN useradd -m -u 1000 user

# Set the working directory
WORKDIR /home/user/app

# Copy the requirements file and install dependencies
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files (including the trained .pkl models)
COPY --chown=user:user . .

# Switch to the non-root user
USER user

# Hugging Face Spaces uses port 7860 by default for Docker spaces
EXPOSE 7860

# Run the FastAPI application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
