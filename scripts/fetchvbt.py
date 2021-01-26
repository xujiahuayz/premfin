import requests
from pickle import dump
from CONST import *

r = requests.get(VBT_URL)

dump(r.content, open(DATA_FOLDER + 'vbt', 'wb'))
