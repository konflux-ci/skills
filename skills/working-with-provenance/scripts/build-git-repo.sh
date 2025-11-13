#!/bin/bash -u

IMAGE=${1}

expression='.payload | @base64d | fromjson | .predicate.buildConfig.tasks[0].invocation.environment.annotations."pipelinesascode.tekton.dev/repo-url"'
cosign download attestation $IMAGE | jq -r "$expression"
