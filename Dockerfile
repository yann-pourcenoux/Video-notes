# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install uv, the package manager
RUN pip install uv

# Copy the project files and install dependencies
COPY pyproject.toml uv.lock* README.md ./
RUN uv sync --no-dev

# Copy the application code
COPY src/ ./src/

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define environment variable to tell Streamlit not to open a browser window
ENV STREAMLIT_SERVER_HEADLESS=true

# Run the app when the container launches
CMD ["uv", "run", "streamlit", "run", "src/video_notes/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
