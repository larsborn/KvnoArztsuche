#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import json
from dataclasses import dataclass, is_dataclass, asdict, field
from typing import List, Optional, Any, Dict


@dataclass
class Phone:
    vorwahl: str
    nummer: str
    is_manueller_datensatz: bool


@dataclass
class Homepage:
    website: str
    is_manueller_datensatz: bool


@dataclass
class Email:
    email_addresse: str
    is_manueller_datensatz: bool


@dataclass
class Person:
    id: int

    strasse: str
    hausnummer: str
    plz: str
    ort: str

    leistungsort_nummer: str
    leistungsort_id: int

    phones: List[Phone]
    homepages: List[Homepage]
    emails: List[Email]
    fax: List[Phone]
    place_longitute: float
    place_latitude: float

    bereiche: List[str]

    title: str
    vorname: Optional[str]
    nachname: Optional[str]
    geschlecht_title: str
    zwischentitel: Optional[str]
    vortitel: Optional[str]
    geschlecht: Optional[int]
    is_privatarzt: bool

    created_at: datetime = field(default_factory=lambda: datetime.datetime.now())

    details: Optional[Dict] = None


class CustomJsonEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if is_dataclass(o):
            return asdict(o)
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        return super().default(o)
