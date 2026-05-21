#!/usr/bin/env python3
"""Detection Log CLI - Elasticsearch 탐지 로그 조회용 Python 스크립트"""

import argparse
import asyncio
import json
import os
import sys

import httpx

ES_ENDPOINT = "https://apik.plex.nexon.io:5502"

ES_INDEX_MAP = {
    "live": "engagement-api-http-access-log-*",
    "stage": "stage-engagement-api-http-access-log-*",
    "pre-stage": "pre-engagement-api-http-access-log-*",
    "dev": "dev-engagement-api-http-access-log-*",
}
ES_INDEX = ES_INDEX_MAP["live"]
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


def get_index(env=None):
    return ES_INDEX_MAP.get(env, ES_INDEX) if env else ES_INDEX


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


async def _es_post(client, body, env=None):
    r = await client.post(
        f"{ES_ENDPOINT}/{get_index(env)}/_search",
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


def _deep_get(d, path, default=None):
    """점으로 구분된 경로로 중첩 dict에서 값을 가져온다."""
    keys = path.split(".")
    for k in keys:
        if isinstance(d, dict):
            d = d.get(k, default)
        else:
            return default
    return d


async def search_logs(args):
    filters = build_filters(args)
    must = []
    if getattr(args, "text", None):
        must.append({"match": {"request.body.data.text": args.text}})

    if getattr(args, "detected", False):
        type_name = getattr(args, "type", None)
        if type_name:
            filters.append({"range": {f"stat.{type_name}.infer_detect": {"gt": 0}}})

    if getattr(args, "undetected", False):
        type_name = getattr(args, "type", None)
        if type_name:
            filters.append({"term": {f"stat.{type_name}.infer_detect": 0}})

    score_min = getattr(args, "score_min", None)
    score_max = getattr(args, "score_max", None)
    if (score_min is not None or score_max is not None):
        type_name = getattr(args, "type", None)
        if type_name:
            score_range = {}
            if score_min is not None:
                score_range["gte"] = score_min
            if score_max is not None:
                score_range["lte"] = score_max
            filters.append({"range": {f"stat.{type_name}.infer_prediction": score_range}})

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
    }

    # --detected/--undetected/--score-range + --type 사용 시 필요 필드만 요청 (출력량 대폭 감소)
    detected = getattr(args, "detected", False)
    undetected = getattr(args, "undetected", False)
    score_min = getattr(args, "score_min", None)
    score_max = getattr(args, "score_max", None)
    type_name = getattr(args, "type", None)
    if (detected or undetected or score_min is not None or score_max is not None) and type_name:
        body["_source"] = [
            "@timestamp",
            "request.body.serviceId",
            "request.body.data.text",
            f"stat.{type_name}.infer_prediction",
        ]
    else:
        body["_source"] = [
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
        ]

    env = getattr(args, "env", None)
    async with httpx.AsyncClient(verify=False) as client:
        data, err = await _es_post(client, body, env)
        if err:
            return err
        hits = data.get("hits", {}).get("hits", [])

        # --detected/--undetected + --type 사용 시 compact 출력
        detected = getattr(args, "detected", False)
        undetected = getattr(args, "undetected", False)
        type_name = getattr(args, "type", None)
        if detected and type_name:
            compact = []
            for h in hits:
                src = h.get("_source", {})
                texts = _deep_get(src, "request.body.data.text", [])
                preds = _deep_get(src, f"stat.{type_name}.infer_prediction", [])
                detected_items = []
                for i, pred in enumerate(preds):
                    if isinstance(pred, (int, float)) and pred >= 0.8:
                        text = texts[i] if i < len(texts) else ""
                        detected_items.append({"text": text, "prediction": round(pred, 4)})
                if detected_items:
                    compact.append({
                        "timestamp": src.get("@timestamp", ""),
                        "service_id": _deep_get(src, "request.body.serviceId", ""),
                        "detected_texts": detected_items,
                    })
            return {
                "total": _total(data),
                "returned": len(compact),
                "results": compact,
            }

        score_min = getattr(args, "score_min", None)
        score_max = getattr(args, "score_max", None)

        if undetected and type_name:
            compact = []
            for h in hits:
                src = h.get("_source", {})
                texts = _deep_get(src, "request.body.data.text", [])
                preds = _deep_get(src, f"stat.{type_name}.infer_prediction", [])
                items = []
                for i, text in enumerate(texts if isinstance(texts, list) else [texts]):
                    pred = preds[i] if isinstance(preds, list) and i < len(preds) else 0
                    items.append({"text": text, "prediction": round(pred, 4) if isinstance(pred, (int, float)) else pred})
                if items:
                    compact.append({
                        "timestamp": src.get("@timestamp", ""),
                        "service_id": _deep_get(src, "request.body.serviceId", ""),
                        "texts": items,
                    })
            return {
                "total": _total(data),
                "returned": len(compact),
                "results": compact,
            }

        if (score_min is not None or score_max is not None) and type_name:
            compact = []
            for h in hits:
                src = h.get("_source", {})
                texts = _deep_get(src, "request.body.data.text", [])
                preds = _deep_get(src, f"stat.{type_name}.infer_prediction", [])
                items = []
                for i, text in enumerate(texts if isinstance(texts, list) else [texts]):
                    pred = preds[i] if isinstance(preds, list) and i < len(preds) else 0
                    if not isinstance(pred, (int, float)):
                        continue
                    in_range = True
                    if score_min is not None and pred < score_min:
                        in_range = False
                    if score_max is not None and pred > score_max:
                        in_range = False
                    if in_range:
                        items.append({"text": text, "prediction": round(pred, 4)})
                if items:
                    compact.append({
                        "timestamp": src.get("@timestamp", ""),
                        "service_id": _deep_get(src, "request.body.serviceId", ""),
                        "texts": items,
                    })
            return {
                "total": _total(data),
                "returned": len(compact),
                "results": compact,
            }

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

    env = getattr(args, "env", None)
    async with httpx.AsyncClient(verify=False) as client:
        data, err = await _es_post(client, body, env)
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

    env = getattr(args, "env", None)
    async with httpx.AsyncClient(verify=False) as client:
        data, err = await _es_post(client, body, env)
        if err:
            return err
        buckets = data.get("aggregations", {}).get("by_type", {}).get("buckets", [])

        # 각 타입의 탐지 건수를 병렬로 조회
        async def _detect_count(type_name):
            detect_filters = filters + [
                {"term": {"request.body.types.keyword": type_name}},
                {"range": {f"stat.{type_name}.infer_detect": {"gt": 0}}},
            ]
            detect_body = {
                "query": {"bool": {"filter": detect_filters}},
                "size": 0,
                "track_total_hits": True,
            }
            d2, _ = await _es_post(client, detect_body)
            return _total(d2) if d2 else 0

        detect_counts = await asyncio.gather(
            *[_detect_count(b["key"]) for b in buckets]
        )

        types_stats = []
        for b, detected in zip(buckets, detect_counts):
            total = b["doc_count"]
            rate = round(detected / total * 100, 2) if total > 0 else 0.0
            types_stats.append(
                {"type": b["key"], "total": total, "detected": detected, "rate_percent": rate}
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

    env = getattr(args, "env", None)
    async with httpx.AsyncClient(verify=False) as client:
        data, err = await _es_post(client, body, env)
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
    parser.add_argument("--env", choices=["live", "stage", "pre-stage", "dev"], default=None,
                        help="ES 인덱스 환경 (기본: live)")


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
    s.add_argument("--undetected", action="store_true",
                   help="미탐 로그만 필터 (--type 필수, stat.{type}.infer_detect == 0)")
    s.add_argument("--score-min", dest="score_min", type=float,
                   help="prediction 하한 필터 (예: 0.5)")
    s.add_argument("--score-max", dest="score_max", type=float,
                   help="prediction 상한 필터 (예: 0.79)")

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
