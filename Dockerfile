FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port Streamlit will run on (Cloud Run default)
EXPOSE 8080

# Make the start script executable
RUN chmod +x start.sh

# Run the start script to launch both backend and frontend
CMD ["./start.sh"]
