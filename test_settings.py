DEBUG = True
TEMPLATE_DEBUG = DEBUG

# For Postgres do from command line
# echo "CREATE USER guinness_vip WITH PASSWORD 'guinness_vip'" | sudo -u postgres psql
# echo "CREATE DATABASE guinness_vip WITH OWNER guinness_vip ENCODING 'UTF8'" | sudo -u postgres psql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_p
        'NAME': 'football365_test.db', # Or path to database file if using sqlite3.
        'USER': '', # Not used with sqlite3.
        'PASSWORD': '', # Not used with sqlite3.
        'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '', # Set to empty string for default. Not used with sqlite3.
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'KEY_PREFIX': 'football365_test',
    }
}

SITE_ID = 1

# need to add gfc after guinness_vip
INSTALLED_APPS = (
    'football365',
)

FOOTBALL365 = {
    'url': 'http://f365-za.com/f',
    'client_id': '',  # put active client id here
    # if a feed is empty, replace the id with that of an active feed
    'test_service_ids': {
        'table': 125,
        'fixtures': 125,
        'results': 125,
        'live': 125
    }
}
