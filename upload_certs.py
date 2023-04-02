from dotenv import load_dotenv
import requests
import argparse
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Upload certificate to CPANEL Host")
    parser.add_argument(
        "--domain",
        "-d",
        required=True,
        help="domain folder in the acmetool live folder",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="output additional information on success",
    )

    args = parser.parse_args()
    load_dotenv()
    cpanel_username = os.environ.get("USERNAME")
    cpanel_api_token = os.environ.get("API_TOKEN")
    cpanel_base_url = os.environ.get("BASE_URL")
    live_base_dir = os.environ.get("LIVE_DIR")
    live_base_path = Path(live_base_dir) / args.domain

    certpath = live_base_path / "cert"
    with certpath.open() as certfile:
        cert = certfile.read()

    keypath = live_base_path / "privkey"
    with keypath.open() as keyfile:
        key = keyfile.read()

    chainpath = live_base_path / "chain"
    with chainpath.open() as chainfile:
        chain = chainfile.read()

    query = {"cert": cert, "key": key, "cabundle": chain, "domain": args.domain}

    url = f"https://{cpanel_base_url}/execute/SSL/install_ssl"
    headers = {
        "Authorization": f"cpanel {cpanel_username}:{cpanel_api_token}",
        "Accept": "application/json",
    }
    r = requests.get(url, params=query, headers=headers, allow_redirects=False)
    if r.status_code != 200:
        raise SystemExit(f"request to {url} failed with status {r.status_code}")

    response_data = r.json()
    if response_data["status"] == 0:
        raise SystemExit(response_data["errors"][0])

    if args.verbose:
        for message in response_data["messages"]:
            print(message)


if __name__ == "__main__":
    main()
