# Step 1: Use Python 3.10 slim image
FROM python:3.10-slim

# Step 2: Set environment variables
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/venv

# Step 3: Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libpq-dev \
    curl \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Step 4: Install Node.js and npm
RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Step 5: Create and activate a virtual environment
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Step 6: Copy Python dependencies and install them
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Step 7: Clone and install additional backend dependencies
COPY autogen /autogen
RUN pip install -e /autogen/python/packages/autogen-magentic-one && \
    pip install -e /autogen/python/packages/autogen-core && \
    pip install -e /autogen/python/packages/autogen-ext

# Step 8: Install and build the React frontend
COPY autobnb-app /app/autobnb-app
WORKDIR /app/autobnb-app
RUN npm install && npm run build

# Step 9: Move frontend build files to Flask static directory
WORKDIR /app
RUN mkdir -p static/build && cp -r autobnb-app/build/* static/build/

# Step 10: Copy the rest of the application files
COPY . /app

# Step 11: Install Playwright dependencies
RUN pip install playwright && playwright install --with-deps

# Step 12: Expose the application port
EXPOSE 5001

# Step 13: Run the Flask application
CMD ["python", "main.py"]
