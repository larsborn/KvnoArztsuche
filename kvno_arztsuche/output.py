#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from dataclasses import dataclass
from typing import Optional

from kvno_arztsuche.model import Person, CustomJsonEncoder


@dataclass
class OutputConfig:
    json_print: bool
    pretty_print: bool
    json_output_file_name: Optional[str]


class Dumper:
    def __init__(self, config: OutputConfig):
        self._config = config

    def line(self, person: Person):
        line = json.dumps(person, cls=CustomJsonEncoder)
        if self._config.json_output_file_name:
            with open(self._config.json_output_file_name, 'a') as fp:
                fp.write(f'{line}\n')
        if self._config.json_print:
            print(line)
        if self._config.pretty_print:
            print(
                f'{"" if person.title is None else person.title} {person.vorname} {person.nachname}, '
                f'{person.strasse} {person.hausnummer}, '
                f'{person.plz} {person.ort}'
                f''.strip()
            )
