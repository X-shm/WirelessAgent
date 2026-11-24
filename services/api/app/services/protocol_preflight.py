"""Check standard-search runtime prerequisites before installing a release."""

import argparse
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--service-pid", type=int, default=0)
    args = parser.parse_args()
    if args.service_pid > 0:
        try:
            entries = Path(f"/proc/{args.service_pid}/environ").read_bytes().split(b"\0")
        except OSError:
            entries = []
        for entry in entries:
            name, _, value = entry.partition(b"=")
            if name in {b"DASHSCOPE_API_KEY", b"CHROMA_PERSIST_DIR", b"DATABASE_URL", b"SECRET_KEY", b"OPENCLAW_API_KEY"} and value:
                os.environ.setdefault(name.decode(), value.decode())

    try:
        import rank_bm25  # noqa: F401
        from app.config import settings
        from app.services.chroma_service import chroma
        from app.services.protocol_index import SOURCE_METADATA_VERSION, open_protocol_index

        if not settings.dashscope_api_key.get_secret_value().strip():
            parser.exit(1, "Standard search preflight failed: DASHSCOPE_API_KEY is missing\n")
        collection = open_protocol_index(chroma.client)
        if collection.metadata.get("source_metadata_version") != SOURCE_METADATA_VERSION:
            parser.exit(1, "Standard search preflight failed: reimport the protocol index with the current importer\n")
    except Exception as error:
        parser.exit(1, f"Standard search preflight failed ({type(error).__name__})\n")
    print(f"Standard search preflight passed: {collection.name}, {collection.count()} chunks")


if __name__ == "__main__":
    main()
