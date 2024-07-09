#!/usr/bin/env python
""" Module returning the meta version using config file """
import json

if __name__ == "__main__":

    # Opening JSON file
    with open('tools/config.json', 'r', encoding='utf-8') as CONFIG_FILE:
        # returns JSON object as a dictionary
        JS_DICT = json.load(CONFIG_FILE)
        print(JS_DICT['meta_version'])
        # close file
        CONFIG_FILE.close()
