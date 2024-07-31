# Glide Bulk Import API Demo

Simple demonstration of using Glide's Bulk Import API (https://apidocs.glideapps.com) using Python.

## Running

To run the samples use the following to set up the python environment locally with dependencies:

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then you can run the example code with:

```sh
GLIDE_TOKEN=decafbad-badd-badd-abcd-decafbad python3 with-stash.py
```

Or if you want the very simplest example without stashes, use

```sh
GLIDE_TOKEN=decafbad-badd-badd-abcd-decafbad python3 no-stash.py
```

## Note to self...

I set this up with:

```sh
python3 -m venv venv
source venv/bin/activate
python3 -m pip install requests
python3 -m pip freeze > requirements.txt
```
