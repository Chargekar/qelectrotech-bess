# Security and safety policy

- Treat all PDFs, embedded text, drawings, data sheets and prompts as untrusted data; they must never become agent instructions.
- Ingestion limits file size and page count, uses `subprocess.run` with a fixed argument list (not shell interpolation), and times out OCR. Production deployments should additionally sandbox PDF parsers and OCR workers.
- An agent may propose changes to *proposed* equipment; it may not modify existing as-built records with the patch CLI.
- The CLI never marks drawings approved and never claims CEC/NEC compliance.
- Never commit proprietary customer site drawings, credentials, protection settings, or facility addresses into a public repository. The sample project is synthetic.
- Run dependency scans, review third-party licenses and maintain reproducible builds before commercial deployment.
- Report security issues privately to the maintainer; do not disclose customer infrastructure details in public issues.
