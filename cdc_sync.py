#!/usr/bin/env python

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nepsenotopi.settings')
django.setup()

from nepse.consumers.cdc_mongo import DBZConsumer

if __name__ == "__main__":
    DBZConsumer().poll_messages()