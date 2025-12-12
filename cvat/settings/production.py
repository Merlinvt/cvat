# Copyright (C) 2018-2022 Intel Corporation
#
# SPDX-License-Identifier: MIT

# Inherit parent config
from .base import *  # pylint: disable=wildcard-import

DEBUG = False

# Allow CSRF trusted origins from environment variable (for development with local UI)
_csrf_origins = os.getenv("CSRF_TRUSTED_ORIGINS", "")
if _csrf_origins:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in _csrf_origins.split(",")]

# CORS settings for local development with separate UI server
_cvat_ui_port = os.getenv("CVAT_UI_PORT", "")
if _cvat_ui_port:
    _ui_origin = f"http://localhost:{_cvat_ui_port}"
    CORS_ALLOWED_ORIGINS = [_ui_origin]
    CORS_ALLOW_CREDENTIALS = True

    # Allow all methods needed for TUS upload protocol
    CORS_ALLOW_METHODS = [
        "DELETE",
        "GET",
        "HEAD",
        "OPTIONS",
        "PATCH",
        "POST",
        "PUT",
    ]

    # Expose headers needed for TUS upload
    CORS_EXPOSE_HEADERS = [
        "location",
        "upload-offset",
        "upload-length",
        "tus-version",
        "tus-resumable",
        "tus-max-size",
        "tus-extension",
    ]

NUCLIO["HOST"] = os.getenv("CVAT_NUCLIO_HOST", "nuclio")

# Django-sendfile:
# https://github.com/moggers87/django-sendfile2
SENDFILE_BACKEND = "django_sendfile.backends.nginx"
SENDFILE_URL = "/"

LOGGING["formatters"]["verbose_uvicorn_access"] = {
    "()": "uvicorn.logging.AccessFormatter",
    "format": '[{asctime}] {levelprefix} {client_addr} - "{request_line}" {status_code}',
    "style": "{",
}
LOGGING["handlers"]["verbose_uvicorn_access"] = {
    "formatter": "verbose_uvicorn_access",
    "class": "logging.StreamHandler",
    "stream": "ext://sys.stdout",
}
LOGGING["loggers"]["uvicorn.access"] = {
    "handlers": ["verbose_uvicorn_access"],
    "level": "INFO",
    "propagate": False,
}
