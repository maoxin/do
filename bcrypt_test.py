#!/usr/bin/env python

import bcrypt
ps = bcrypt.hashpw("someyahoogoogle765", bcrypt.gensalt())

for i in range(50):
    print ps == bcrypt.hashpw("someyahoogoogle765", ps)