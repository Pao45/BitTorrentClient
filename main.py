from threading import Thread, Condition
from Downloader import Downloader
from Uploader import Uploader 
import socket

buf = []
Downloader(buf).start() 
Uploader(buf).start()
