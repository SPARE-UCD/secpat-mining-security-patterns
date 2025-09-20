import os

class LibrariesIOConfig:
    API_KEY = os.getenv("LIBRARIES_IO_API_KEY")
    max_num_pages = 100
    max_per_page = 100