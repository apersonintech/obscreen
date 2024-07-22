#!/usr/bin/python3
import os

from src.Application import Application

if __name__ == '__main__':
    app = Application(application_dir=os.path.dirname(__file__))
    app.start()
