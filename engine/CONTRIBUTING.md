# Contributing

1. Keep every engineering assumption explicit and preserve provenance.
2. Write tests for topology validators, solvers and drawing output when adding capabilities.
3. Do not infer missing field ratings or claim regulatory compliance from solver output.
4. Use separate example fixtures; never add a customer's proprietary drawings.
5. Submit changes with a clear description, deterministic test result, and limitations.

Run `python -m pytest -q` after installing `pip install -e '.[dev,draw,ingest]'`.
