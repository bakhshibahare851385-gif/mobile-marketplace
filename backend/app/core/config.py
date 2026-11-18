"""Application configuration read from the environment."""

import os

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-secret-replace-before-deployment")
