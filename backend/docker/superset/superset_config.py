"""
Apache Superset Configuration File

This configuration connects Superset to the OneStep PostgreSQL database
and configures caching, security, and feature flags.
"""

import os
from typing import Optional

# Superset specific config
ROW_LIMIT = 5000

# Flask App Builder configuration
# Your App secret key will be used for securely signing the session cookie
# and encrypting sensitive information on the database
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY', 'your-superset-secret-key-change-in-production')

# The SQLAlchemy connection string to your database backend
# This connection defines where Superset stores its metadata (dashboards, charts, users, etc.)
SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{os.environ.get('DATABASE_USER', 'postgres')}:"
    f"{os.environ.get('DATABASE_PASSWORD', 'postgres')}@"
    f"{os.environ.get('DATABASE_HOST', 'db')}:"
    f"{os.environ.get('DATABASE_PORT', '5432')}/"
    f"{os.environ.get('DATABASE_DB', 'superset')}"
)

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = True

# Add endpoints that need to be exempt from CSRF protection
WTF_CSRF_EXEMPT_LIST = []

# A CSRF token that expires in 1 year
WTF_CSRF_TIME_LIMIT = 60 * 60 * 24 * 365

# Set this API key to enable Mapbox visualizations
MAPBOX_API_KEY = os.environ.get('MAPBOX_API_KEY', '')

# Redis configuration for caching and async queries
REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = os.environ.get('REDIS_PORT', '6379')

# Cache configuration
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 1,
}

# Data cache configuration
DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,  # 24 hours
    'CACHE_KEY_PREFIX': 'superset_data_',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_REDIS_PORT': REDIS_PORT,
    'CACHE_REDIS_DB': 2,
}

# Async query configuration using Celery
class CeleryConfig:
    broker_url = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
    imports = ('superset.sql_lab',)
    result_backend = f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
    worker_prefetch_multiplier = 1
    task_acks_late = False
    task_annotations = {
        'sql_lab.get_sql_results': {
            'rate_limit': '100/s',
        },
    }

CELERY_CONFIG = CeleryConfig

# Feature flags
FEATURE_FLAGS = {
    'ENABLE_TEMPLATE_PROCESSING': True,
    'ENABLE_TEMPLATE_REMOVE_FILTERS': True,
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True,
    'DASHBOARD_NATIVE_FILTERS_SET': True,
    'EMBEDDABLE_CHARTS': True,
    'SCHEDULED_QUERIES': True,
    'SQL_VALIDATORS_BY_ENGINE': True,
    'ALERT_REPORTS': True,
}

# Security configuration
# Uncomment to setup Full admin role name
# AUTH_ROLE_ADMIN = 'Admin'

# Uncomment to setup Public role name, no authentication needed
# AUTH_ROLE_PUBLIC = 'Public'

# Will allow user self registration
AUTH_USER_REGISTRATION = True

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = "Public"

# When using LDAP Auth, setup the LDAP server
# AUTH_TYPE = AUTH_LDAP
# AUTH_LDAP_SERVER = "ldap://ldapserver.new"

# Uncomment to setup OpenID providers example for OpenID authentication
# OPENID_PROVIDERS = [
#    { 'name': 'Yahoo', 'url': 'https://me.yahoo.com' },
#    { 'name': 'Flickr', 'url': 'https://www.flickr.com/<username>' },
# ]

# Timeout duration for SQL Lab queries
SQLLAB_TIMEOUT = 300  # 5 minutes

# Async query timeout
SQLLAB_ASYNC_TIME_LIMIT_SEC = 600  # 10 minutes

# SQL query validation
SQL_MAX_ROW = 100000

# Default row limit for SQL Lab
DEFAULT_SQLLAB_LIMIT = 1000

# Enable/Disable SQL Lab
ENABLE_JAVASCRIPT_CONTROLS = False

# CSV export encoding
CSV_EXPORT = {
    'encoding': 'utf-8',
}

# Webdriver configuration for alerts and reports
# Uncomment and configure if you want to enable alerts/reports
# WEBDRIVER_BASEURL = "http://superset:8088/"
# WEBDRIVER_BASEURL_USER_FRIENDLY = "http://localhost:8088/"

# Email configuration for alerts
# SMTP_HOST = "smtp.gmail.com"
# SMTP_STARTTLS = True
# SMTP_SSL = False
# SMTP_USER = "your-email@gmail.com"
# SMTP_PORT = 587
# SMTP_PASSWORD = "your-password"
# SMTP_MAIL_FROM = "your-email@gmail.com"

# Slack configuration for alerts
# SLACK_API_TOKEN = "xoxb-your-slack-token"

# Allow for javascript controls components
# This enables programmers to customize certain charts (like the
# geospatial ones) by inputting javascript in controls. This exposes
# an XSS security vulnerability
ENABLE_JAVASCRIPT_CONTROLS = False

# Allowed file extensions for file upload
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'txt'}

# Maximum file size for uploads (in bytes)
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

# Dashboard position JSON size limit
DASHBOARD_POSITION_DATA_LIMIT = 65535

# Superset dashboard auto-refresh intervals (in seconds)
SUPERSET_DASHBOARD_POSITION_DATA_LIMIT = 65535

# Custom OAuth2 configuration (if needed)
# from flask_appbuilder.security.manager import AUTH_OAUTH
# AUTH_TYPE = AUTH_OAUTH
# OAUTH_PROVIDERS = [
#     {
#         'name': 'google',
#         'icon': 'fa-google',
#         'token_key': 'access_token',
#         'remote_app': {
#             'client_id': 'GOOGLE_CLIENT_ID',
#             'client_secret': 'GOOGLE_CLIENT_SECRET',
#             'api_base_url': 'https://www.googleapis.com/oauth2/v2/',
#             'client_kwargs': {'scope': 'email profile'},
#             'request_token_url': None,
#             'access_token_url': 'https://accounts.google.com/o/oauth2/token',
#             'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
#         },
#     }
# ]

# Logging configuration
ENABLE_TIME_ROTATE = True
TIME_ROTATE_LOG_LEVEL = 'INFO'
FILENAME = os.path.join('/app/superset_home', 'superset.log')

# Console logging
ENABLE_CONSOLE_LOG = True
CONSOLE_LOG_LEVEL = 'INFO'

# Sentry configuration (optional)
# SENTRY_DSN = os.environ.get('SENTRY_DSN')
# if SENTRY_DSN:
#     import sentry_sdk
#     from sentry_sdk.integrations.flask import FlaskIntegration
#     sentry_sdk.init(
#         dsn=SENTRY_DSN,
#         integrations=[FlaskIntegration()],
#         traces_sample_rate=0.1
#     )
