"""
This module processes openapi schema yaml files in order
to retrieve descriptions and summaries of endpoints
"""
import re
from typing import List, Dict
import yaml
import json


def normalize_schema(schema: Dict):

    path_elements = [{"to_replace": r'\$\{MODEL_NAME\}', "replacement": "{model_name}"},
                     {"to_replace": r'\$\{MODEL_VERSION\}', "replacement": "{model_version}"},
                     {"to_replace": r'/v2/$', "replacement": "/v2"}]
    # normalize paths
    for element in path_elements:
        for path in list(schema['paths'].keys()):
            if 'parameters' in schema['paths'][path]:
                #for i in schema['paths'][path]['parameters']:
                print(schema['paths'][path]['parameters'])
            #path = re.sub(element["to_replace"], element["replacement"], path
            schema['paths'][re.sub(element["to_replace"], element["replacement"], path)] = schema['paths'].pop(path)
   # print(schema['paths'][path]['parameters'])


    # normalize schema keys
    schemas = {}
    for schema_comp in list(schema['components']['schemas'].keys()):

        #schema['components']['schemas'][schema_comp.title().replace("_", "")] = schema['components']['schemas'][schema_comp].pop(schema_comp)
        key = schema_comp.title().replace("_", "")
        schemas[key] = schema_comp
        schema['components']['schemas'][key] = schema['components']['schemas'].pop(schema_comp)
        schema['components']['schemas'][key]['title'] = key


    new_schema = json.dumps(schema)

    for key, value in schemas.items():
        to_replace = '#/components/schemas/' + value
        replacement = '#/components/schemas/' + key

        new_schema = new_schema.replace(to_replace, replacement)

   # print("inside normalize")
   # print(new_schema)

    return new_schema



def merge_schemas(path_1: str, path_2: str) -> Dict[str, str]:
    """
        Method used to merge API paths and schemas of two openapi yaml files.
        The paths are taken in as parameters.
        It returns a dictionary of merged schemas.
    """
    #TODO handle normalization here
    with open(path_1) as file:
        schema_1 = yaml.load(file, Loader=yaml.FullLoader)
    schema_1 = json.loads(normalize_schema(schema_1))
    #print("inside merge1")
    #print(schema_1)

    with open(path_2) as file:
        schema_2 = yaml.load(file, Loader=yaml.FullLoader)
    schema_2 = json.loads(normalize_schema(schema_2))
    #print("inside merge2")
    #print(schema_2)



    merged_schema = schema_1.copy()
    merged_schema['paths'].update(schema_2['paths'])
    merged_schema['components']['schemas'].update(schema_2['components']['schemas'])

    with open('openapi/toyaml.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(merged_schema, file, sort_keys=False)

    return merged_schema
