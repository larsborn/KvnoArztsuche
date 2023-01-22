#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
from typing import Optional, Iterator

import requests
import requests.adapters
from urllib3 import Retry

from kvno_arztsuche.model import Person, Phone, Homepage, Email


class CustomHTTPAdapter(requests.adapters.HTTPAdapter):
    def __init__(
            self,
            fixed_timeout: int = 5,
            retries: int = 3,
            backoff_factor: float = 0.3,
            status_forcelist=(500, 502, 504),
            pool_maxsize: Optional[int] = None
    ):
        self._fixed_timeout = fixed_timeout
        retry_strategy = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        kwargs = {'max_retries': retry_strategy}
        if pool_maxsize is not None:
            kwargs['pool_maxsize'] = pool_maxsize
        super().__init__(**kwargs)

    def send(self, *args, **kwargs):
        if kwargs['timeout'] is None:
            kwargs['timeout'] = self._fixed_timeout
        return super(CustomHTTPAdapter, self).send(*args, **kwargs)


class Endpoint:
    def __init__(self, base_url: str = 'https://arztsuche.kvno.de/api/api/'):
        self.places = f'{base_url}places'
        self.places_possiblefilters = f'{base_url}places/possiblefilters'
        self.person = f'{base_url}person/{"{}"}'


class ApiException(Exception):
    pass


class ConsoleHandler(logging.Handler):
    def emit(self, record):
        print('[%s] %s' % (record.levelname, record.msg))


class KvnoArztsucheApi:
    def __init__(self, logger: logging.Logger, user_agent: str):
        self._logger = logger
        self._endpoint = Endpoint()
        self._session = requests.session()
        self._session.mount('https://', CustomHTTPAdapter())
        self._session.mount('http://', CustomHTTPAdapter())
        self._session.headers = {'User-Agent': user_agent}

    def details(self, person: Person) -> Person:
        response = self._session.get(self._endpoint.person.format(person.id))
        response.raise_for_status()
        person.details = response.json()

        return person

    def search(self, near: int = 1000, page_size=100000, address: str = '') -> Iterator[Person]:
        page = 1
        while True:
            self._logger.debug(f'Reading page {page}...')
            response = self._session.post(
                self._endpoint.places,
                json={
                    "searchText": "",
                    "near": near,
                    "address": address,
                    "page": page,
                    "pageSize": page_size,
                    "UserLocation": {"Lat": 0, "Lng": 0},
                    "filterModel": {
                        "fremdsprachenFilter": [],
                        "geschlechtFilter": [],
                        "fachgebieteFilter": [],
                        "schwerpunkteFilter": [],
                        "zusatzbezeichnungFilter": [],
                        "behandlungsprogrammFilter": [],
                        "psychotherapieVerfahrenFilter": [
                            # "Analytische Psychotherapie f^ür Erwachsene",
                            # "Systemische Psychotherapie f^ür Erwachsene",
                            # "Tiefenpsychologisch fundierte Psychotherapie f^ür Erwachsene",
                            # "Verhaltenstherapie f^ür Erwachsene",
                        ],
                        "barrierefreiheitFilter": [],
                        "erreichbarkeitTagFilter": [],
                        "erreichbarkeitZeitFilter": [],
                    }
                }
            )
            response.raise_for_status()
            page += 1
            data = response.json()
            person_list = data.get('personList', [])
            if len(person_list) == 0:
                break
            for row in person_list:
                ignored_fields = {'distance'}
                processed_fields = {
                    'id',
                    'title',
                    'strasse',
                    'plz',
                    'ort',
                    'bereiche',
                    'telefonvorwahl',
                    'telefonnummer',
                    'isManuellerDatensatz',
                    'phone',
                    'webSite',
                    'isManuellerDatensatz',
                    'homePage',
                    'emailAddress',
                    'isManuellerDatensatz',
                    'email',
                    'faxvorwahl',
                    'faxnummer',
                    'isManuellerDatensatz',
                    'fax',
                    'geschlectTitle',
                    'zwischentitel',
                    'vortitel',
                    'vorname',
                    'nachname',
                    'geschlect',
                    'place',
                    'place',
                    'leistungsortnummer',
                    'leistungsortId',
                    'hausnummer',
                    'isPrivatarzt',
                }
                missing_fields = set(row.keys()) - processed_fields.union(ignored_fields)
                if len(missing_fields) > 0:
                    self._logger.error(f'Missing fields: {", ".join(missing_fields)}')

                yield Person(
                    id=row.get('id'),
                    title=row.get('title'),
                    strasse=row.get('strasse'),
                    plz=row.get('plz'),
                    ort=row.get('ort'),
                    bereiche=[bereich for bereich in row.get('bereiche', [])],
                    phones=[Phone(
                        vorwahl=sub_row.get('telefonvorwahl'),
                        nummer=sub_row.get('telefonnummer'),
                        is_manueller_datensatz=sub_row.get('isManuellerDatensatz'),
                    ) for sub_row in row.get('phone')],
                    homepages=[Homepage(
                        website=sub_row.get('webSite'),
                        is_manueller_datensatz=sub_row.get('isManuellerDatensatz'),
                    ) for sub_row in row.get('homePage')],
                    emails=[Email(
                        email_addresse=sub_row.get('emailAddress'),
                        is_manueller_datensatz=sub_row.get('isManuellerDatensatz'),
                    ) for sub_row in row.get('email')],
                    fax=[Phone(
                        vorwahl=sub_row.get('faxvorwahl'),
                        nummer=sub_row.get('faxnummer'),
                        is_manueller_datensatz=sub_row.get('isManuellerDatensatz'),
                    ) for sub_row in row.get('fax')],
                    geschlecht_title=row.get('geschlectTitle'),
                    zwischentitel=row.get('zwischentitel'),
                    vortitel=row.get('vortitel'),
                    vorname=row.get('vorname'),
                    nachname=row.get('nachname'),
                    geschlecht=row.get('geschlect'),
                    place_longitute=row.get('place', {}).get('longitute'),
                    place_latitude=row.get('place', {}).get('latitude'),
                    leistungsort_nummer=row.get('leistungsortnummer'),
                    leistungsort_id=row.get('leistungsortId'),
                    hausnummer=row.get('hausnummer'),
                    is_privatarzt=row.get('isPrivatarzt'),
                )
