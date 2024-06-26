#########################
# Build front end       #
#########################
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package.json .
COPY yarn.lock .
RUN yarn install --frozen-lockfile

COPY babel.config.js .
COPY webpack.config.js .
COPY assets ./assets

RUN yarn run build

#########################
# App image             #
#########################
FROM python:3.10-alpine

# Create app user and group
RUN addgroup -S app && adduser -S app -G app

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
RUN apk add --virtual build-deps gcc musl-dev python3-dev \
  && apk add --no-cache postgresql-dev \
  && pip install --no-cache-dir psycopg2 \
  && apk del build-deps

RUN pip install --no-cache-dir gunicorn==21.2.0

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy front end from builder image
COPY --from=0 /app/static ./static
COPY --from=0 /app/webpack-stats.json .

# Copy code
COPY manage.py .
COPY curation_portal ./curation_portal

# Run as app user
RUN chown -R app:app .
USER app

# Run
# Worker and thread count set according to gunicorn docs
# https://docs.gunicorn.org/en/stable/design.html#how-many-workers
CMD ["gunicorn", \
  "--bind", ":8000", \
  "--log-file", "-", \
  "--workers", "3", "--threads", "1", "--worker-class", "gthread", \
  "--worker-tmp-dir", "/dev/shm", \
  "curation_portal.wsgi"]
