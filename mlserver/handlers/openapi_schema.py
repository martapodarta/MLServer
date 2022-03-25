"""
This module processes openapi schema yaml files in order
to retrieve descriptions and summaries of endpoints
"""
import re
from typing import List, Dict
import yaml
import json


def normalize_schema(openapi_schema: Dict):

    path_elements = [{"to_replace": r'\$\{MODEL_NAME\}', "replacement": "{model_name}"},
                     {"to_replace": r'\$\{MODEL_VERSION\}', "replacement": "{model_version}"},
                     {"to_replace": r'/v2/$', "replacement": "/v2"}]

    # normalize paths and path parameters names
    for element in path_elements:
        for path in list(openapi_schema['paths'].keys()):
            if 'parameters' in openapi_schema['paths'][path]:
                for parameter in openapi_schema['paths'][path]['parameters']:
                    parameter['name'] = parameter['name'].lower()
                    print(parameter['name'])
            openapi_schema['paths'][re.sub(element["to_replace"], element["replacement"], path)] = openapi_schema['paths'].pop(path)

    # normalize schema objects names and titles under components node
    schemas = {}
    for schema_object in list(openapi_schema['components']['schemas'].keys()):
        normalized_schema_name = schema_object.title().replace("_", "")
        openapi_schema['components']['schemas'][normalized_schema_name] = openapi_schema['components']['schemas'].pop(schema_object)
        openapi_schema['components']['schemas'][normalized_schema_name]['title'] = normalized_schema_name
        schemas[normalized_schema_name] = schema_object

    # normalize schema #ref elements across whole document
    openapi_schema = json.dumps(openapi_schema)
    for key, value in schemas.items():
        openapi_schema = openapi_schema.replace('#/components/schemas/' + value, '#/components/schemas/' + key)

    return json.loads(openapi_schema)



def merge_schemas(path_1: str, path_2: str) -> Dict[str, str]:
    """
        Method used to merge API paths and schemas of two openapi yaml files.
        The paths are taken in as parameters.
        It returns a dictionary of merged schemas.
    """
    #TODO handle normalization here
    with open(path_1) as file:
        schema_1 = yaml.load(file, Loader=yaml.FullLoader)
    schema_1 = normalize_schema(schema_1)

    with open(path_2) as file:
        schema_2 = yaml.load(file, Loader=yaml.FullLoader)
    schema_2 = normalize_schema(schema_2)

    merged_schema = schema_1.copy()
    merged_schema['paths'].update(schema_2['paths'])
    merged_schema['components']['schemas'].update(schema_2['components']['schemas'])

    with open('openapi/toyaml.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(merged_schema, file, sort_keys=False)

    return merged_schema
