import os

# PostgreSQL
DB_HOST = "tmatch_db"
DB_PORT = 5432
DB_NAME = os.environ.get("DB_NAME", "")
DB_USER = os.environ.get("DB_USER", "")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# LDAP 
LDAP_HOST = os.environ.get("LDAP_HOST", "")
LDAP_PORT = os.environ.get("LDAP_PORT", "")
LDAP_USER = os.environ.get("LDAP_USER", "")
LDAP_PASSWORD = os.environ.get("LDAP_PASSWORD", "")
LDAP_BASE_DN = os.environ.get("LDAP_BASE_DN", "")

# Email
SMTP_SERVER = os.environ.get("SMTP_SERVER", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
