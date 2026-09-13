# Safe report 187 runtime validation

This researcher-owned disposable repository contains only a harmless marker
and a loopback fake Anthropic API. It validates whether a pull-request-controlled
`tools:` include can read a generated custom-tool catalog from `$RUNNER_TEMP`
and place its description in `ant apply --dry-run` output.

No Anthropic production request, real API key, secret, third-party repository,
or destructive operation is used.
