#!/bin/bash -u

IMAGE=${1}

cosign download attestation $IMAGE \
	| jq -r '.payload | @base64d | fromjson | .predicate.buildConfig.tasks[0].invocation.environment.annotations."pipelinesascode.tekton.dev/log-url"' \
	| sed 's|console.redhat.com/application-pipeline|konflux-ui.apps.stone-prd-rh01.pg1f.p1.openshiftapps.com|'
