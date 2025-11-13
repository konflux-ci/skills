#!/bin/bash -u

IMAGE=${1}

expression='.payload | @base64d | fromjson | .predicate.buildConfig.tasks[0].invocation.environment.annotations | ."pipelinesascode.tekton.dev/repo-url" + "/-/commit/" + ."pipelinesascode.tekton.dev/sha"'
output=$(cosign download attestation $IMAGE | jq -r "$expression")

if [[ "$output" == *github.com/* ]] ; then
	echo "🐙 $output" | sed 's|/-/|/|'
else
	echo "🦊 $output"
fi
