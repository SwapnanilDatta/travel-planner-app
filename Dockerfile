FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app/

# Switch to the travel app directory
WORKDIR /app/travel

# (Skipping collectstatic during build phase to avoid missing environment variable errors)

# Expose port
EXPOSE 8000

# Run Daphne (ASGI server for Django Channels)
CMD ["sh", "-c", "python manage.py collectstatic --no-input && python manage.py migrate && daphne -b 0.0.0.0 -p ${PORT:-8000} travel.asgi:application"]
