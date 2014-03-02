#!/usr/bin/env python

from passlib.hash import bcrypt
ps = bcrypt.encrypt("someyahoogoogle765")

for i in range(50):
    print bcrypt.verify("someyahoogoogle765", ps)