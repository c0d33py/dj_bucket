import ftplib
from django.core.files.base import File
from django.core.files.storage import Storage


class FTPStorage(Storage):
    def __init__(self, host, username, password, *args, **kwargs):
        self.host = host
        self.username = username
        self.password = password

    def _open(self, name, mode='rb'):
        # Open the file on FTP and return a file object
        pass

    def _save(self, name, content):
        # Save the file to FTP
        pass

    def delete(self, name):
        # Delete the file from FTP
        pass

    def exists(self, name):
        # Check if the file exists on FTP
        pass

    def listdir(self, path):
        # List the contents of a directory on FTP
        pass

    def size(self, name):
        # Return the size of a file on FTP
        pass
