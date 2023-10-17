#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
from dataclasses import dataclass
from typing import Optional

from kvno_arztsuche.model import Person, CustomJsonEncoder
from kvno_arztsuche.nsq import Nsq, NsqNoop


@dataclass
class OutputConfig:
    json_print: bool
    pretty_print: bool
    json_output_file_name: Optional[str]
    nsq_topic: Optional[str]
    nsqd_address: Optional[str]
    nsqd_port: Optional[int]


class Dumper:
    def __init__(self, logger: logging.Logger, config: OutputConfig):
        self._config = config
        self._nsq = (Nsq if config.nsqd_address else NsqNoop)(logger, config.nsqd_address, config.nsqd_port)

    def line(self, person: Person):
        self._nsq.publish_person('kvno_arztsuche', person)

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
