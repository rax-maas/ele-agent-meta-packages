#!/usr/bin/env python
""" Module returning the meta version using config file """
import json

if __name__ == "__main__":

    # Opening JSON file
    CONFIG_FILE = open('config.json')

    # returns JSON object as a dictionary
    JS_DICT = json.load(CONFIG_FILE)

    print JS_DICT['meta_version']

    # close file
    CONFIG_FILE.close()
