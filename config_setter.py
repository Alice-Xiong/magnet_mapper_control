import json

# Temporary, will have UI here
settings = {
    'test' :  {
        'radius' : 50,
        'xy_spacing' : 5,
        'x_offset' : 10,
        'y_offset' : 10,
        'depth' : 50,
        'z_spacing' : 10,
        'z_offset' : 0
    }
}

with open('config.json', 'w') as outfile:
    json.dump(settings, outfile)
