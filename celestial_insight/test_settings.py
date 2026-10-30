import os

from .settings import *  # noqa: F403

# The PydanticAI agents construct an OpenAI client at import time. Tests never call the
# provider (interpretation tests inject a fake), so a placeholder keeps the suite hermetic
# instead of depending on a developer's shell or a ~/.env file.
os.environ.setdefault("OPENAI_API_KEY", "test-key-not-used")

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
