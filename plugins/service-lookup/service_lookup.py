#!/usr/bin/env python3
"""Service Lookup CLI - NXLOG/BWS 서비스 ID 조회"""

import argparse
import asyncio
import json
import os
import sys

import httpx

NXLOG_SERVICE_URL = "https://console-extapi.na.nexon.com/console/api/external/liveserviceid"
NXLOG_SERVICE_USER = os.getenv("NXLOG_SERVICE_USER", "")
NXLOG_SERVICE_PASSWORD = os.getenv("NXLOG_SERVICE_PASSWORD", "")

BWS_SERVICE_URL = "https://private.api.nexon.com/inference_sidecar/service_list"
INFERENCE_API_KEY = os.getenv("INFERENCE_API_KEY", "")


async def lookup(query, source="all"):
    query_lower = query.lower() if query else ""
    results = []

    async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
        # NXLOG 서비스 목록 (회사 전체 게임 서비스 ID)
        if source in ("all", "nxlog"):
            try:
                r = await client.get(
                    NXLOG_SERVICE_URL,
                    auth=(NXLOG_SERVICE_USER, NXLOG_SERVICE_PASSWORD),
                )
                if r.status_code == 200:
                    for svc in r.json():
                        game = svc.get("gameName", "")
                        country = svc.get("countryName", "")
                        sid = str(svc.get("serviceID", ""))
                        env = svc.get("commonCodeDesc", "")
                        label = f"{game} ({country})" if country else game
                        if query_lower and query_lower not in label.lower() and query_lower not in sid:
                            continue
                        results.append({
                            "service_id": sid,
                            "name": label,
                            "env": env,
                            "source": "nxlog",
                        })
                else:
                    results.append({"error": f"nxlog API returned {r.status_code}", "source": "nxlog"})
            except Exception as e:
                results.append({"error": f"nxlog API failed: {e}", "source": "nxlog"})

        # BWS/탐지 API 서비스 목록
        if source in ("all", "bws"):
            try:
                r = await client.post(
                    BWS_SERVICE_URL,
                    headers={"x-inface-api-key": INFERENCE_API_KEY},
                )
                if r.status_code == 200:
                    for svc in r.json().get("response", []):
                        memo = svc.get("memo", "")
                        sid = str(svc.get("service_id", ""))
                        stype = svc.get("type", "")
                        if query_lower and query_lower not in memo.lower() and query_lower not in sid:
                            continue
                        results.append({
                            "service_id": sid,
                            "name": memo,
                            "type": stype,
                            "source": "bws",
                        })
                else:
                    results.append({"error": f"bws API returned {r.status_code}", "source": "bws"})
            except Exception as e:
                results.append({"error": f"bws API failed: {e}", "source": "bws"})

    return {"query": query or "", "count": len(results), "results": results}


def main():
    if not NXLOG_SERVICE_USER or not NXLOG_SERVICE_PASSWORD:
        print(json.dumps({"error": "NXLOG_SERVICE_USER / NXLOG_SERVICE_PASSWORD not set"}))
        sys.exit(1)
    if not INFERENCE_API_KEY:
        print(json.dumps({"error": "INFERENCE_API_KEY not set"}))
        sys.exit(1)

    p = argparse.ArgumentParser(description="Service Lookup CLI")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("search", help="서비스 ID 검색")
    s.add_argument("query", nargs="?", default="", help="검색어 (게임명, 메모, 서비스ID)")
    s.add_argument("--source", choices=["all", "nxlog", "bws"], default="all",
                   help="조회 소스 (all: 전체, nxlog: NXLOG만, bws: BWS/탐지API만)")

    a = p.parse_args()

    if a.cmd == "search":
        r = asyncio.run(lookup(a.query, a.source))
    else:
        r = {"error": f"Unknown command: {a.cmd}"}

    print(json.dumps(r, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
