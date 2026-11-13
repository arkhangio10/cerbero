#!/usr/bin/env bash
PYTHONIOENCODING=utf-8 exec python "<repo>/dev/agent_eval/harness.py" --session "<repo>/dev/agent_eval/runs-1.2.1/AG06/state" "$@"
