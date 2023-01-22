# KvnoArztsuche Scraper

This is a scraper for the search of "Kassenärztliche Vereinigung Nordrhein (KVNO)" reachable under 
https://arztsuche.kvno.de/. Output format is JSON that you can then easily search or generate stats.

## Usage

```
usage: service.py [-h] [--debug] [--json-print] [--pretty-print] [--json-output-file-name JSON_OUTPUT_FILE_NAME] [--user-agent USER_AGENT]

optional arguments:
  -h, --help            show this help message and exit
  --debug
  --json-print
  --pretty-print
  --json-output-file-name JSON_OUTPUT_FILE_NAME
  --user-agent USER_AGENT
```

## Example

The following will generate an `output.jsonl`:

```
> SET PYTHONPATH=C:\Path\To\KvnoArztsuche\
> .\kvno_arztsuche\service.py --debug --json-output-file-name output.jsonl
```

Distribution across the 10 cities with the most doctors:  

```bash
$ cat kvno_arztsuche/output.jsonl | jq '.ort' -r | sort | uniq -c | sort -n | tail -n 10
    597 Leverkusen
    760 Krefeld
    820 Mönchengladbach
    898 Aachen
   1001 Wuppertal
   1030 Duisburg
   1397 Essen
   1517 Bonn
   2148 Düsseldorf
   3957 Köln
```
