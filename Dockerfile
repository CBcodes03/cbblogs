FROM python:3.10-alpine

# Set the working directory
WORKDIR /app

COPY . /app
# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port your app runs on
EXPOSE 5000

# Run the app
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development

# Run the Flask app
CMD ["flask", "run"]
