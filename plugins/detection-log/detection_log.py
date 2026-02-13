#!/usr/bin/env python3
"""Detection Log CLI - Elasticsearch 탐지 로그 조회용 Python 스크립트"""

import argparse
import asyncio
import json
import os
import sys

import httpx

ES_ENDPOINT = "https://apik.plex.nexon.io:5502"
ES_INDEX = "engagement-api-http-access-log-*"
ES_USER = os.getenv("ES_USER", "engagement-api-http-access-log-api")
ES_PASSWORD = os.getenv("ES_PASSWORD")


REGION_PATH_PREFIX = {
    "seoul": "/inference/textclassifier",
    "tokyo": "/inference/tyo/",
    "hongkong": "/inference/hkg/",
    "oregon": "/inference/org/",
    "singapore": "/inference/sin/",
    "frankfurt": "/inference/fra/",
}


def get_auth():
    return (ES_USER, ES_PASSWORD)


def build_time_filter(from_time, to_time):
    return {"range": {"@timestamp": {"gte": from_time, "lte": to_time}}}


def build_filters(args):
    filters = [
        build_time_filter(
            getattr(args, "from_time", None) or "now-1h",
            getattr(args, "to_time", None) or "now",
        )
    ]
    if getattr(args, "service_id", None):
        filters.append({"term": {"request.body.serviceId": args.service_id}})
    if getattr(args, "type", None):
        filters.append({"term": {"request.body.types.keyword": args.type}})
    if getattr(args, "path", None):
        filters.append({"term": {"request.path": args.path}})
    if getattr(args, "status", None):
        filters.append({"term": {"response.status": args.status}})
    if getattr(args, "region", None):
        region = args.region.lower()
        prefix = REGION_PATH_PREFIX.get(region)
        if prefix:
            if region == "seoul":
                # 서울은 리전 코드 없이 /inference/textclassifier 또는 /inference/textclassifier_big
                filters.append(
                    {
                        "bool": {
                            "should": [
                                {"term": {"request.headers.x-envoy-original-path": "/inference/textclassifier"}},
                                {"term": {"request.headers.x-envoy-original-path": "/inference/textclassifier_big"}},
                            ],
                            "minimum_should_match": 1,
                        }
                    }
                )
            else:
                filters.append({"prefix": {"request.headers.x-envoy-original-path": prefix}})
    return filters


async def _es_post(client, body):
    r = await client.post(
        f"{ES_ENDPOINT}/{ES_INDEX}/_search",
        auth=get_auth(),
        json=body,
        headers={"Content-Type": "application/json"},
        timeout=30.0,
    )
    if r.status_code != 200:
        return None, {"error": r.status_code, "detail": r.text}
    return r.json(), None


def _total(data):
    t = data.get("hits", {}).get("total", {})
    return t.get("value", 0) if isinstance(t, dict) else t


async def search_logs(args):
    filters = build_filters(args)
    must = []
    if getattr(args, "text", None):
        must.append({"match": {"request.body.data.text": args.text}})

    if getattr(args, "detected", False):
        type_name = getattr(args, "type", None)
        if type_name:
            filters.append({"range": {f"stat.{type_name}.infer_detect": {"gt": 0}}})

    sort_parts = args.sort.split(":")
    sort_field = sort_parts[0]
    sort_order = sort_parts[1] if len(sort_parts) > 1 else "desc"

    body = {
        "query": {
            "bool": {
                "filter": filters,
                "must": must if must else [{"match_all": {}}],
            }
        },
        "size": args.size,
        "sort": [{sort_field: {"order": sort_order}}],
        "_source": [
            "@timestamp",
            "request.path",
            "request.body.serviceId",
            "request.body.types",
            "request.body.data.text",
            "request.body.data.len",
            "request.headers.x-envoy-original-path",
            "response.status",
            "process_time",
            "region",
            "stat",
        ],
    }

    async with httpx.AsyncClient(verify=False) as client:
        data, err = await _es_post(client, body)
        if err:
            return err
        hits = data.get("hits", {}).get("hits", [])
        return {
            "total": _total(data),
            "returned": len(hits),
            "results": [h.get("_source", {}) for h in hits],
        }


async def stats_service(args):
    filters = build_filters(args)
    body = {
        "query": {"bool": {"filter": filters}},
        "size": 0,
        "aggs": {
            "by_service": {
                "terms": {
                    "field": "request.body.serviceId",
                    "size": args.size,
                    "order": {"_count": "desc"},
                }
            }
        },
    }

    async with httpx.AsyncClient(verify=False) as client:
        data, err = await _es_post(client, body)
        if err:
            return err
        buckets = data.get("aggregations", {}).get("by_service", {}).get("buckets", [])
        return {
            "total_logs": _total(data),
            "service_count": len(buckets),
            "services": [{"service_id": b["key"], "count": b["doc_count"]} for b in buckets],
        }


async def stats_type(args):
    filters = build_filters(args)
    body = {
        "query": {"bool": {"filter": filters}},
        "size": 0,
        "aggs": {
            "by_type": {
                "terms": {
                    "field": "request.body.types.keyword",
                    "size": args.size,
                    "order": {"_count": "desc"},
                }
            }
        },
    }

    async with httpx.AsyncClient(verify=False) as client:
        data, err = await _es_post(client, body)
        if err:
            return err
        buckets = data.get("aggregations", {}).get("by_type", {}).get("buckets", [])

        types_stats = []
        for b in buckets:
            type_name = b["key"]
            total = b["doc_count"]

            # stat 필드에서 . 을 포함한 중첩 경로로 조회
            detect_filters = filters + [
                {"term": {"request.body.types.keyword": type_name}},
                {"range": {f"stat.{type_name}.infer_detect": {"gt": 0}}},
            ]
            detect_body = {
                "query": {"bool": {"filter": detect_filters}},
                "size": 0,
                "track_total_hits": True,
            }
            d2, err2 = await _es_post(client, detect_body)
            detected = _total(d2) if d2 else 0
            rate = round(detected / total * 100, 2) if total > 0 else 0.0
            types_stats.append(
                {"type": type_name, "total": total, "detected": detected, "rate_percent": rate}
            )

        return {"types": types_stats}


async def stats_timeline(args):
    filters = build_filters(args)
    interval = getattr(args, "interval", None) or "1h"
    body = {
        "query": {"bool": {"filter": filters}},
        "size": 0,
        "aggs": {
            "timeline": {
                "date_histogram": {
                    "field": "@timestamp",
                    "fixed_interval": interval,
                    "format": "yyyy-MM-dd HH:mm:ss",
                    "time_zone": "Asia/Seoul",
                }
            }
        },
    }

    async with httpx.AsyncClient(verify=False) as client:
        data, err = await _es_post(client, body)
        if err:
            return err
        buckets = data.get("aggregations", {}).get("timeline", {}).get("buckets", [])
        return {
            "interval": interval,
            "buckets": [{"time": b.get("key_as_string"), "count": b["doc_count"]} for b in buckets],
        }


def _add_common_args(parser):
    parser.add_argument("-f", "--from", dest="from_time", default="now-1h")
    parser.add_argument("-t", "--to", dest="to_time", default="now")
    parser.add_argument("-s", "--service-id", dest="service_id")
    parser.add_argument("--type")
    parser.add_argument("-r", "--region")
    parser.add_argument("-n", "--size", type=int, default=20)


def main():
    if not ES_PASSWORD:
        print(json.dumps({"error": "ES_PASSWORD environment variable is not set"}))
        sys.exit(1)

    p = argparse.ArgumentParser(description="Detection Log CLI")
    sp = p.add_subparsers(dest="cmd", required=True)

    # search
    s = sp.add_parser("search")
    _add_common_args(s)
    s.add_argument("--path")
    s.add_argument("--status", type=int)
    s.add_argument("--sort", default="@timestamp:desc")
    s.add_argument("--text")
    s.add_argument("--detected", action="store_true",
                   help="탐지된 로그만 필터 (--type 필수, stat.{type}.infer_detect > 0)")

    # stats
    st = sp.add_parser("stats")
    st_sub = st.add_subparsers(dest="stats_type", required=True)

    ss = st_sub.add_parser("service")
    _add_common_args(ss)

    sty = st_sub.add_parser("type")
    _add_common_args(sty)

    stl = st_sub.add_parser("timeline")
    _add_common_args(stl)
    stl.add_argument("--interval", default="1h")

    a = p.parse_args()

    if a.cmd == "search":
        r = asyncio.run(search_logs(a))
    elif a.cmd == "stats":
        if a.stats_type == "service":
            r = asyncio.run(stats_service(a))
        elif a.stats_type == "type":
            r = asyncio.run(stats_type(a))
        elif a.stats_type == "timeline":
            r = asyncio.run(stats_timeline(a))
        else:
            r = {"error": f"Unknown stats type: {a.stats_type}"}
    else:
        r = {"error": f"Unknown command: {a.cmd}"}

    print(json.dumps(r, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
