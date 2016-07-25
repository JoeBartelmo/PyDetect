import json
import sys
from StringIO import StringIO

compare_structure = './structure.json'

def validate_json(json_data):
    print 'Validating...'
    try:
        json_data = json.load(StringIO(json_data))
    except:
        print 'Failure parsing JSON'
        return False
    with open(compare_structure) as legend:
        legend = json.load(legend)
        for key in legend:
            if key not in json_data:
                print key + ' not in sent data'
                return False
        if any(key not in legend for key in json_data):
            return False
    return True

