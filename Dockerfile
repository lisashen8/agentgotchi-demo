FROM node:20-slim

# Install Python 3 and required tools
RUN apt-get update && \
    apt-get install -y python3 python3-pip python3-venv curl && \
    rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment to avoid PEP 668 restrictions
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Pre-install the Python dependencies required by the backend
RUN pip install streamlit google-genai google-adk

# Set the working directory
WORKDIR /app

# Copy package configurations first to leverage Docker cache
COPY package.json ./

# Install Node dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build the Express TypeScript server
RUN npm run build

# Start the application
CMD ["npm", "start"]
