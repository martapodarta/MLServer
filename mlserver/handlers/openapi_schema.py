import yaml
import re


def get_schema():

    with open('api_docs/openapi.yaml') as f:
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
                    endpoint["path"] = normalize_paths(path)
                    print(endpoint["path"])
                    endpoint["operation"] = operation
                    endpoint["desc"] = description
                    endpoint["summary"] = summary
                    endpoints.append(endpoint)

        return endpoints


def normalize_paths(path: str):

    path_elements = [{"to_replace": r'\$\{MODEL_NAME\}',
                      "replacement": "{model_name}"},
                     {"to_replace": r'\$\{MODEL_VERSION\}',
                      "replacement": "{model_version}"},
                     {"to_replace": r'/v2/$',
                      "replacement": "/v2"},
                                        ]
    for element in path_elements:
        path = re.sub(element["to_replace"], element["replacement"], path)

    return path

