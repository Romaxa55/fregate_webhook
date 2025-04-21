#!/bin/bash
helm upgrade --install motion-listener ./motion-listener -n frigate -f ./motion-listener/values.yaml --create-namespace
