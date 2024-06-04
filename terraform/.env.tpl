MODE=${MODE}

DB_HOST=${POSTGRES_HOST}
DB_PORT=${POSTGRES_PORT}
DB_NAME=${POSTGRES_DB}
DB_USER=${POSTGRES_USER}
DB_PASS=${POSTGRES_PASSWORD}
DB_SSLMODE=verify-full

REDIS_URL=redis://:${REDIS_PASSWORD}@${REDIS_HOST}:${REDIS_PORT}

SECRET_KEY_JWT=${SECRET_KEY_JWT}
SECRET_VERIFICATION_TOKEN=${SECRET_VERIFICATION_TOKEN}
SECRET_RESET_TOKEN=${SECRET_RESET_TOKEN}

BACKEND_URL=http://${BACKEND_IP}

QUEUE_URL=${QUEUE_URL}
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
BUCKET_NAME=${BUCKET_NAME}