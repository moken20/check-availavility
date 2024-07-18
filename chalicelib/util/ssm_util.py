import ast
from typing import Dict, List

import boto3
from aws_lambda_powertools import Logger

logger = Logger(child=True) 

ssm = boto3.client('ssm')


def get_parameter_store(name: str):
    response = ssm.get_parameter(Name=name, WithDecryption=True)
    available_rooms = ast.literal_eval(response["Parameter"]["Value"])
    logger.info(f"Get data from parameter store: {available_rooms}")

    return available_rooms


def update_parameter_store(name: str, value: Dict[str, List[str]]):
    str_value = str(value)
    ssm.put_parameter(Name=name, Value=str_value, Type="String", Overwrite=True)
    logger.info(f"Put data in parameter store: {str_value}")
