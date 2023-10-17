#!/usr/bin/env python3
import argparse
import logging
import os
import platform
from collections import defaultdict

import requests
import requests.adapters

__version__ = '1.0.0'

from kvno_arztsuche.api import ApiException, ConsoleHandler, KvnoArztsucheApi
from kvno_arztsuche.output import Dumper, OutputConfig


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--json-print', action='store_true')
    parser.add_argument('--pretty-print', action='store_true')
    parser.add_argument('--json-output-file-name')
    parser.add_argument('--nsq-topic', default=os.getenv('NSQ_TOPIC', 'kvno_arztsuche'))
    parser.add_argument('--nsqd-address', default=os.getenv('NSQD_ADDRESS'))
    parser.add_argument('--nsqd-port', default=os.getenv('NSQD_PORT', '4151'), type=int)
    parser.add_argument(
        '--user-agent',
        default=F'KvnoArztsucheScraper/{__version__} (python-requests {requests.__version__}) '
                F'{platform.system()} ({platform.release()})'
    )
    args = parser.parse_args()

    logger = logging.getLogger('KvnoArztsucheScraper')
    logger.handlers.append(ConsoleHandler())
    logger.setLevel(logging.DEBUG if args.debug else logging.INFO)

    logger.debug(F'Using User-Agent string: {args.user_agent}')
    api = KvnoArztsucheApi(logger, args.user_agent)
    dumper = Dumper(logger, OutputConfig(
        json_print=args.json_print,
        pretty_print=args.pretty_print,
        json_output_file_name=args.json_output_file_name,
        nsq_topic=args.nsq_topic,
        nsqd_address=args.nsqd_address,
        nsqd_port=args.nsqd_port,
    ))
    by_ort = defaultdict(int)
    try:
        i = 0
        for person in api.search():
            by_ort[person.ort] += 1
            person = api.details(person)
            dumper.line(person)
            i += 1
        logger.info(f'Scraped {i} rows.')
        for ort, cnt in sorted(by_ort.items(), key=lambda item: item[1]):
            logger.info(f'{ort}: {cnt}')
    except ApiException as e:
        logger.exception(e)
    except requests.exceptions.ConnectionError as e:
        logger.exception(e)


if __name__ == '__main__':
    main()
