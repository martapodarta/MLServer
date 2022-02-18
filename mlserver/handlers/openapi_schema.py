import json
import yaml

def get_schema():
    # Opening JSON file
    #f = open('/Users/martamazur/Documents/aia/MLServer/openapi/target.json')

    with open('/Users/martamazur/Documents/martapodarta/MLServer/openapi/dataplane.yaml') as f:
        schema = yaml.load(f)
        #print(schema)
        data = {}
        for path in schema['paths']:  # for key, value in paths.iteritems():
            #print(path)  # get API paths
            for operation in schema['paths'][path]:
                #print(operation)
                if operation not in ["parameters"]:
                    desc = schema['paths'][path][operation]['description']
                    summary= schema['paths'][path][operation]['summary']
                    #print(desc)
                    #print(summary)

                    data[f"'paths']['{path}']['{operation}']['description'"] = desc
        #print(data)
        keys = list(data.keys())
        #print(keys)

        return data

        #keys = list(data.keys())
        #print(keys)
