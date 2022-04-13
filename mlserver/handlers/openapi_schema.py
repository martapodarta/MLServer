from typing import Dict
import yaml


def merge_schemas(path_1: str, path_2: str) -> Dict[str, str]:
    """
        Method used to merge API paths and schemas of two openapi yaml files.
        The paths are taken in as parameters.
        It returns a dictionary of merged schemas.
    """

    with open(path_1) as file:
        schema_1 = yaml.load(file, Loader=yaml.FullLoader)

    with open(path_2) as file:
        schema_2 = yaml.load(file, Loader=yaml.FullLoader)

    merged_schema = schema_1.copy()
    merged_schema['paths'].update(schema_2['paths'])
    merged_schema['components']['schemas'].update(schema_2['components']['schemas'])

    return merged_schema
