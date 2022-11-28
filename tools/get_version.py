#!/usr/bin/env python

import json

if __name__ == "__main__":


    # Opening JSON file
    f = open('config.json')

    # returns JSON object as a dictionary
    js = json.load(f)

    print(js['meta_version'])

