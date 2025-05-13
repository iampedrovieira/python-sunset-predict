#Create a test file that save a txt file in current directory
# with hello world

import os
from dotenv import load_dotenv

file_name = os.getenv("TEST_FILE_NAME")
with open(f'{file_name}.txt', 'w') as f:
    f.write('Hello World')