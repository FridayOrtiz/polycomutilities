#!/bin/bash
# Install dependencies

echo 'Installing dependencies for Polycom Utilities.'

sudo apt-get update && sudo apt-get install xlsx2csv && echo 'Successfully installed dependencies.'
