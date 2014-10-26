# Directory where CTD stores its database
ENGINE_DIR = r'c:\temp\comp'
# Directory where CTD temporarily stores uploaded images until moving them to IMAGES_DIR
TEMP_UPLOAD_DIR = r'c:\temp\tempimg'
# Directory where CTD stores uploaded images
IMAGES_DIR = r'c:\temp\img'
# Directory where CTD stores generated thumbnails
THUMBNAIL_DIR = r'c:\temp\thumbs'

# Number of last submitted images to a series to calculate series stability rating
COMMIT_COUNT_FOR_STABILITY = 10
# CTD server name
SERVER_NAME = '127.0.0.1:5000'

# File where CTD stores e-mail database
ALERT_FILE = r'c:\temp\emails.txt'
# SMTP server
EMAIL_SERVER = 'localhost'
# From address for e-mails sent by CTD
EMAIL_FROM = 'ctd@example.com'
# Subject field for e-mails sent by CTD
EMAIL_SUBJECT = 'Image series are unstable'
# Number of minutes between sending new e-mails
EMAIL_PERIOD = 1