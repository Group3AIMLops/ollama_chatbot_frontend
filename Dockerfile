# Base image for a Python environment
FROM python:3.9  
# Adjust Python version if needed

# Set the working directory
WORKDIR /app

# Copy project files
COPY ./api/ api/
COPY config.yml config.yml
COPY user_products.csv user_products.csv
COPY requirement.txt requirement.txt

RUN ls

# Install dependencies from requirements.txt
RUN pip install -r requirement.txt

EXPOSE 8501

# Run the main application file on container startup
CMD ["streamlit", "run", "api/app.py"]