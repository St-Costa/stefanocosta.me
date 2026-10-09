#!/usr/bin/env python3
"""
Preflight R2: verifica che le credenziali S3 funzionino e mostra il contenuto
dei due bucket (stdlib + boto3). Le credenziali NON vanno mai nel repo:
solo env o prompt interattivo.

Uso (credenziali dell'R2 API token, endpoint jurisdiction-specific EU):
  R2_ACCESS_KEY_ID=... R2_SECRET_ACCESS_KEY=... \\
  R2_ENDPOINT=https://<account>.r2.cloudflarestorage.com \\
      python3 scripts/r2_check.py

Variabile mancante -> chiesta al prompt (getpass: niente history della shell).
Serve boto3 una tantum: pip install boto3
"""
import os
import sys


def get(name, secret=False):
    val = os.environ.get(name)
    if val:
        return val
    if secret:
        import getpass
        return getpass.getpass(f"{name}: ")
    return input(f"{name}: ")


BUCKETS = ("stefanocosta-documents", "stefanocosta-audio")


def main():
    try:
        import boto3
        import botocore
    except ImportError:
        sys.exit("manca boto3: pip install boto3")
    s3 = boto3.client(
        "s3",
        endpoint_url=get("R2_ENDPOINT"),
        aws_access_key_id=get("R2_ACCESS_KEY_ID"),
        aws_secret_access_key=get("R2_SECRET_ACCESS_KEY", secret=True),
        region_name="auto",
    )
    ok = True
    for bucket in BUCKETS:
        try:
            n, total, token = 0, 0, None
            while True:
                kw = {"Bucket": bucket}
                if token:
                    kw["ContinuationToken"] = token
                resp = s3.list_objects_v2(**kw)
                for obj in resp.get("Contents", []):
                    n += 1
                    total += obj["Size"]
                token = resp.get("NextContinuationToken")
                if not token:
                    break
            print(f"{bucket}: {n} oggetti, {total // 1024}KB")
        except botocore.exceptions.ClientError as e:
            ok = False
            print(f"{bucket}: ERRORE {e.response['Error'].get('Code')}: "
                  f"{e.response['Error'].get('Message')}")
    if not ok:
        sys.exit(1)
    print("collegamento S3 ok.")


if __name__ == "__main__":
    main()
