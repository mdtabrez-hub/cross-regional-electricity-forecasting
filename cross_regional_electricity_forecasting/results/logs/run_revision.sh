#!/bin/bash
set -e
cd "$(dirname "$0")/../.."
python3 -u -m src.revision_experiments ridge
python3 -u -m src.revision_experiments excluded
python3 -u -m src.revision_experiments origins
python3 -u -m src.revision_experiments spatial
echo REVISION_DONE
