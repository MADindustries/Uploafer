USERNAME = 'your PTH username'
PASSWORD = 'your PTH password'
ANNOUNCE = 'your PTH announce URL'

WM2_ROOT = 'path to directory containing "manage.py" from WM2'  #for auto importing after upload
WM2_MEDIA = 'path to WM2 media directory'  #directories should be labeled by ID per WM2 standard operation
WORKING_ROOT = 'path to a working directory'  #will only contain one torrent/media pair at a time. must be writable. may also contain resume files
FUZZ_RATIO = 90  #Match likeness threshold. Above (or equal) will be ignored as a dup. Below will await user interaction