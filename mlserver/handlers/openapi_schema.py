import json
import yaml

def get_schema():

    with open('/Users/martamazur/Documents/martapodarta/MLServer/openapi/dataplane.yaml') as f:
        schema = yaml.load(f, Loader=yaml.FullLoader)

        endpoints = []

        # get API paths
        for path in schema['paths']:
            path_node = schema['paths'][path]
            # operations supported by openapi 3.0
            operations = ["get", "post", "put", "patch", "delete", "head", "options", "trace"]
            for node in path_node:
                if node in operations:
                    endpoint = {}
                    operation = node
                    description = schema['paths'][path][operation]['description']
                    summary = schema['paths'][path][operation]['summary']
                    endpoint["path"] = path
                    endpoint["operation"] = operation
                    endpoint["desc"] = description
                    endpoint["summary"] = summary
                    endpoints.append(endpoint)

        #print(endpoints)

        return endpoints


