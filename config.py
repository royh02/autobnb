# OpenAI model settings
MODEL_NAME = "gpt-4o-mini"
TEMPERATURE = 0.9

# Worker settings
MAX_WORKERS = 5

# Max listings to search for
MAX_LISTING_COUNT = 10
SHOWN_LISTING_COUNT = 6

# Flask port
FLASK_PORT = 5001

# Weights for ranking
DESCRIPTION_WEIGHT = 0.8
IMAGE_WEIGHT = 1 - DESCRIPTION_WEIGHT

# Database stuff
DATABASE = 'database.db'