FROM python:3.12-slim

# Create a non-root user and group
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /code

COPY requirements.txt .
# Upgrade pip and install dependencies as root
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY ./app ./app

# Change ownership to non-root user
RUN chown -R appuser:appgroup /code

EXPOSE 8000

# Switch to non-root user
USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
