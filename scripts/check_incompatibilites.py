
"""
Verifie la symetrie des incompatibilites d'implants exposees par NeuroLink-API.

Regle metier attendue : si A est incompatible avec B, alors B est incompatible
avec A. La relation doit etre symetrique.

Usage
-----
  # contre l'API en cours d'execution
  set NEUROLINK_API_KEY=sk_xxx_xxx          (Windows / PowerShell : $env:NEUROLINK_API_KEY="...")
  python check_incompatibilites.py

  # contre un dump JSON deja enregistre
  python check_incompatibilites.py --file reponse_implants.json

Variables d'environnement
-------------------------
  NEUROLINK_URL      base de l'API        (defaut : http://localhost:8010)
  NEUROLINK_API_KEY  cle API, role User suffisant

Code de sortie : 0 si la relation est symetrique, 1 sinon.
Aucune dependance externe (stdlib uniquement).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT_URL = os.environ.get("NEUROLINK_URL", "http://localhost:8000")
API_KEY = os.environ.get("NEUROLINK_API_KEY")
ENDPOINT = "/api/v1/implants/"


def fetch_from_api(base_url: str, api_key: str) -> list[dict]:
    url = base_url.rstrip("/") + ENDPOINT
    request = urllib.request.Request(url, headers={"X-API-Key": api_key})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        sys.exit(f"HTTP {error.code} sur {url} : {error.read().decode('utf-8', 'replace')[:200]}")
    except urllib.error.URLError as error:
        sys.exit(f"Impossible de joindre {url} : {error.reason}")


def load_from_file(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def build_graph(implants: list[dict]) -> dict[str, set[str]]:
    """reference -> ensemble des references declarees incompatibles."""
    graph: dict[str, set[str]] = {}
    for implant in implants:
        reference = implant["reference"]
        prerequisites = implant.get("prerequisites") or {}
        incompatible = prerequisites.get("incompatibleImplants") or []
        graph[reference] = set(incompatible)
    return graph


def find_asymmetries(graph: dict[str, set[str]]) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Retourne (paires_non_reciproques, references_inconnues)."""
    asymmetric: list[tuple[str, str]] = []
    unknown: list[tuple[str, str]] = []

    for source, targets in graph.items():
        for target in sorted(targets):
            if target not in graph:
                unknown.append((source, target))
                continue
            if source not in graph[target]:
                asymmetric.append((source, target))

    return sorted(asymmetric), sorted(unknown)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--file", help="analyser un dump JSON au lieu d'interroger l'API")
    parser.add_argument("--url", default=DEFAULT_URL, help=f"base de l'API (defaut : {DEFAULT_URL})")
    parser.add_argument("--limit", type=int, default=10, help="nombre de paires detaillees affichees")
    parser.add_argument("--api_key", help="Cle API (defaut : NEUROLINK_API_KEY)")
    args = parser.parse_args()

    if args.file:
        implants = load_from_file(args.file)
        source_label = args.file
    else:
        implants = fetch_from_api(args.url, args.api_key)
        source_label = args.url.rstrip("/") + ENDPOINT

    graph = build_graph(implants)
    total_edges = sum(len(targets) for targets in graph.values())
    asymmetric, unknown = find_asymmetries(graph)

    print(f"Source              : {source_label}")
    print(f"Implants analyses   : {len(graph)}")
    print(f"Relations declarees : {total_edges}")
    print(f"Non reciproques     : {len(asymmetric)}")
    print(f"References inconnues: {len(unknown)}")
    print()

    if unknown:
        print("References citees mais absentes du catalogue :")
        for source, target in unknown[: args.limit]:
            print(f"  {source} -> {target} (introuvable)")
        print()

    if not asymmetric:
        print("OK : la relation d'incompatibilite est symetrique.")
        return 0

    print(f"Paires non reciproques (les {min(args.limit, len(asymmetric))} premieres) :")
    for source, target in asymmetric[: args.limit]:
        print(f"  {source} -> {target}   mais   {target} -> {sorted(graph[target])}")

    if len(asymmetric) > args.limit:
        print(f"  ... et {len(asymmetric) - args.limit} autres")

    print()
    print("ECHEC : la relation d'incompatibilite n'est pas symetrique.")
    return 1


if __name__ == "__main__":
    #raise SystemExit(main())
    main()