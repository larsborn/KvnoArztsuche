#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Dict, Optional

import requests

from kvno_arztsuche.model import Person, CustomJsonEncoder


@dataclass
class ClientSideCertificate:
    crt_path: str
    key_path: str


def id_for_person(person: Person) -> str:
    data = json.loads(json.dumps(person, indent=0, cls=CustomJsonEncoder))
    del data['created_at']
    hash_digest = hashlib.sha256(json.dumps(data, indent=0, sort_keys=True).encode('utf-8')).hexdigest()
    return hash_digest[:8]


class NsqNoop:
    def __init__(
            self,
            logger: logging.Logger,
            _nsqd_address: str,
            _nsqd_write_port: int = 4151,
            _cert: Optional[ClientSideCertificate] = None,
    ):
        self._logger = logger

    def publish_person(self, topic: str, person: Person) -> None:
        self._logger.warning(f'Not publishing {id_for_person(person)}/{person.id} to "{topic}"')


class Nsq:
    def __init__(
            self,
            logger: logging.Logger,
            nsqd_address: str,
            nsqd_write_port: int = 4151,
            cert: Optional[ClientSideCertificate] = None,
    ):
        self._logger = logger
        self._nsqd_address = nsqd_address
        self._nsqd_write_port = nsqd_write_port
        self._session = requests.session()
        if cert:
            self._session.cert = (cert.crt_path, cert.key_path)

    def publish_dict(self, topic: str, message: Dict) -> None:
        return self.publish(topic, json.dumps(message))

    def publish(self, topic: str, message: str) -> None:
        self.publish_bytes(topic, message.encode('utf-8'))

    def publish_bytes(self, topic: str, message: bytes) -> None:
        response = self._session.post(
            F'http://{self._nsqd_address}:{self._nsqd_write_port}/pub?topic={topic}',
            data=message
        )
        response.raise_for_status()

    def publish_person(self, topic: str, person: Person) -> None:
        row = json.loads(json.dumps(person, indent=0, cls=CustomJsonEncoder, sort_keys=True))
        row['_key'] = id_for_person(person)
        self.publish_dict(topic, row)
