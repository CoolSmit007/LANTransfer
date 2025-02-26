import logging
import os
import re
from dataclasses import dataclass

import yaml
from typing import Dict
from pydantic import BaseModel, ValidationError


@dataclass
class FileConfigs:
    chunkSize: int

@dataclass
class AppConfig(BaseModel):
    fileConfigs: FileConfigs
    socketBufferSize: int

def load_config():
    """Loads configuration from a YAML file and environment variables."""

    file_name = 'application.yml'

    with open(file_name, "r") as file:
        data = yaml.safe_load(file)

    # Create DTO instance, using Pydantic for parsing and validation
    return AppConfig.parse_obj(data)


CONFIGS = load_config()
