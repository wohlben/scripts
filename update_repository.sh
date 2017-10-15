#!/bin/bash

REPO_PATH=$1

echo $REPO_PATH
if [ -z ${REPO_PATH} ]; then
  echo "no repo path given"
  exit 1
else
  cd ${REPO_PATH}
  git pull > /dev/null
fi

