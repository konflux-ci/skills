#!/bin/bash -u

IMAGE=${1}

expression='.payload | @base64d | fromjson | .subject[0].name + ":" + .predicate.buildConfig.tasks[0].invocation.environment.annotations."pipelinesascode.tekton.dev/sha"'
output=$(cosign download attestation $IMAGE | jq -r "$expression")

echo $output
