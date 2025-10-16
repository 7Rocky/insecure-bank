#!/bin/bash

docker build -t insecure-bank .
docker run -p 5000:5000 --rm --name insecure-bank insecure-bank