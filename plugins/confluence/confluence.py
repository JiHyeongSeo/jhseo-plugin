#!/usr/bin/env python3
"""Confluence CLI - 독립적인 스킬용 Python 스크립트"""

import argparse
import asyncio
import json
import os
import sys

import httpx

CONFLUENCE_URL = "https://confluence.nexon.com"
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
ALLOWED_SPACE_KEYS = ["NAD"]
ALLOWED_PAGE_IDS = ["2674833208"]


def get_auth_header():
    return {"Authorization": f"Bearer {CONFLUENCE_API_TOKEN}", "Content-Type": "application/json"}


def is_allowed(page_id, ancestors=None):
    if not ALLOWED_PAGE_IDS:
        return True
    if str(page_id) in ALLOWED_PAGE_IDS:
        return True
    if ancestors:
        for a in ancestors:
            if str(a.get("id") if isinstance(a, dict) else a) in ALLOWED_PAGE_IDS:
                return True
    return False


def _has_result_descendant(nodes, node_id, result_ids):
    """해당 노드가 검색 결과이거나 검색 결과를 자손으로 갖는지 여부"""
    if node_id in result_ids:
        return True
    node = nodes.get(node_id)
    if not node:
        return False
    for cid in node.get("children", []):
        if _has_result_descendant(nodes, cid, result_ids):
            return True
    return False


def _build_result_tree(nodes, node_id, result_ids, pre="", last=True, depth=0, max_depth=6):
    """검색 결과만 강조하고, 그 외 형제는 '...'로 접은 트리 문자열"""
    if depth > max_depth or node_id not in nodes:
        return ""
    node = nodes[node_id]
    branch = "└── " if last else "├── "
    line = f"{pre}{branch}{node['title']}\n"
    child_pre = pre + ("    " if last else "│   ")
    children = node.get("children", [])
    # 검색 결과이거나 검색 결과를 자손으로 갖는 자식만 표시
    displayed = [c for c in children if c in result_ids or _has_result_descendant(nodes, c, result_ids)]
    in_other_run = False
    displayed_idx = 0
    for cid in children:
        if cid in result_ids:
            in_other_run = False
            displayed_idx += 1
            is_last = displayed_idx == len(displayed)
            cn = nodes.get(cid, {})
            line += f"{child_pre}{'└── ' if is_last else '├── '}{cn.get('title', '?')}\n"
        elif _has_result_descendant(nodes, cid, result_ids):
            in_other_run = False
            displayed_idx += 1
            is_last = displayed_idx == len(displayed)
            line += _build_result_tree(nodes, cid, result_ids, child_pre, is_last, depth + 1, max_depth)
        else:
            if not in_other_run:
                line += f"{child_pre}...\n"
                in_other_run = True
    return line


async def _enrich_nodes_with_ancestors(client, nodes, root_ids, result_ids):
    """검색 결과 페이지들의 ancestors를 조회해서 root→검색결과 경로를 nodes에 채움"""
    for page_id in result_ids:
        if not page_id:
            continue
        try:
            r = await client.get(f"{CONFLUENCE_URL}/rest/api/content/{page_id}",
                                 headers=get_auth_header(), params={"expand": "ancestors"})
            if r.status_code != 200:
                continue
            data = r.json()
            ancestors = data.get("ancestors", [])
            pid = str(data.get("id", ""))
            if pid not in nodes:
                nodes[pid] = {"title": data.get("title", "?"), "children": []}

            # ALLOWED_PAGE_IDS가 ancestors에 있으면 거기서부터 시작
            allowed_idx = -1
            if ALLOWED_PAGE_IDS:
                for i, anc in enumerate(ancestors):
                    if str(anc.get("id", "")) in ALLOWED_PAGE_IDS:
                        allowed_idx = i
                        break

            # allowed_idx부터 끝까지만 트리에 포함
            start_idx = allowed_idx if allowed_idx >= 0 else 0
            for i in range(start_idx, len(ancestors)):
                anc = ancestors[i]
                aid = str(anc.get("id", ""))
                if not aid:
                    continue
                if aid not in nodes:
                    nodes[aid] = {"title": anc.get("title", "?"), "children": []}
                child_id = str(ancestors[i + 1]["id"]) if i + 1 < len(ancestors) else pid
                if child_id not in nodes[aid]["children"]:
                    nodes[aid]["children"].append(child_id)

            # root_ids에 추가
            if allowed_idx >= 0:
                root_ids.add(str(ancestors[allowed_idx].get("id", "")))
            elif ancestors:
                root_ids.add(str(ancestors[0].get("id", "")))
        except Exception:
            continue
    # children 정렬
    for n in nodes.values():
        n["children"].sort(key=lambda c: nodes.get(c, {}).get("title", ""))


async def search(query, space=None, limit=25):
    async with httpx.AsyncClient() as c:
        cql = f'type=page AND text~"{query}"'
        if space:
            cql += f' AND space.key="{space}"'
        r = await c.get(f"{CONFLUENCE_URL}/rest/api/content/search", headers=get_auth_header(),
                        params={"cql": cql, "limit": limit, "expand": "space,ancestors"})
        if r.status_code != 200:
            return {"error": r.status_code, "detail": r.text}

        raw_pages = r.json().get("results", [])
        pages = []
        for p in raw_pages:
            if is_allowed(p.get("id"), p.get("ancestors", [])):
                pages.append({
                    "id": p.get("id"),
                    "title": p.get("title"),
                    "url": f"{CONFLUENCE_URL}/pages/viewpage.action?pageId={p.get('id')}"
                })

        result_ids = {str(p["id"]) for p in pages}

        # 트리 구성을 위한 노드 수집
        nodes = {}
        root_ids = set()

        # 검색 결과의 ancestors를 조회해서 트리 경로 구성
        await _enrich_nodes_with_ancestors(c, nodes, root_ids, result_ids)

        # result_tree 생성
        result_tree = ""
        if result_ids and nodes:
            sorted_roots = sorted(root_ids, key=lambda r: nodes.get(r, {}).get("title", ""))
            lines = []
            for i, rid in enumerate(sorted_roots):
                if rid not in nodes or not _has_result_descendant(nodes, rid, result_ids):
                    continue
                is_last = i == len(sorted_roots) - 1
                lines.append(_build_result_tree(nodes, rid, result_ids, "", is_last))
            result_tree = "".join(lines).strip()

        return {"total": len(pages), "pages": pages, "result_tree": result_tree}


async def get_page(page_id):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{CONFLUENCE_URL}/rest/api/content/{page_id}", headers=get_auth_header(),
                        params={"expand": "body.storage,ancestors,version,space"})
        if r.status_code != 200:
            return {"error": r.status_code}
        d = r.json()
        if not is_allowed(page_id, d.get("ancestors", [])):
            return {"error": "not allowed"}
        return {"id": d.get("id"), "title": d.get("title"), "content": d.get("body", {}).get("storage", {}).get("value", ""),
                "version": d.get("version", {}).get("number"), "url": f"{CONFLUENCE_URL}/pages/viewpage.action?pageId={page_id}"}


async def create(space, title, content, parent=None):
    async with httpx.AsyncClient() as c:
        data = {"type": "page", "title": title, "space": {"key": space},
                "body": {"storage": {"value": content, "representation": "storage"}}}
        if parent:
            data["ancestors"] = [{"id": parent}]
        r = await c.post(f"{CONFLUENCE_URL}/rest/api/content", headers=get_auth_header(), json=data)
        if r.status_code not in (200, 201):
            return {"error": r.status_code, "detail": r.text}
        d = r.json()
        return {"success": True, "id": d.get("id"), "url": f"{CONFLUENCE_URL}/pages/viewpage.action?pageId={d.get('id')}"}


async def update(page_id, title=None, content=None):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{CONFLUENCE_URL}/rest/api/content/{page_id}", headers=get_auth_header(),
                        params={"expand": "body.storage,version,space,ancestors"})
        if r.status_code != 200:
            return {"error": r.status_code}
        d = r.json()
        if not is_allowed(page_id, d.get("ancestors", [])):
            return {"error": "not allowed"}
        data = {"id": page_id, "type": "page", "title": title or d.get("title"),
                "space": {"key": d.get("space", {}).get("key")},
                "body": {"storage": {"value": content or d.get("body", {}).get("storage", {}).get("value"), "representation": "storage"}},
                "version": {"number": d["version"]["number"] + 1}}
        r = await c.put(f"{CONFLUENCE_URL}/rest/api/content/{page_id}", headers=get_auth_header(), json=data)
        if r.status_code != 200:
            return {"error": r.status_code, "detail": r.text}
        return {"success": True, "id": page_id}


async def label_add(page_id, label_name):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{CONFLUENCE_URL}/rest/api/content/{page_id}", headers=get_auth_header(),
                        params={"expand": "ancestors"})
        if r.status_code != 200:
            return {"error": r.status_code}
        d = r.json()
        if not is_allowed(page_id, d.get("ancestors", [])):
            return {"error": "not allowed"}
        r = await c.post(f"{CONFLUENCE_URL}/rest/api/content/{page_id}/label", headers=get_auth_header(),
                         json=[{"prefix": "global", "name": label_name}])
        if r.status_code not in (200, 201):
            return {"error": r.status_code, "detail": r.text}
        return {"success": True, "id": page_id, "label": label_name}


async def label_remove(page_id, label_name):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{CONFLUENCE_URL}/rest/api/content/{page_id}", headers=get_auth_header(),
                        params={"expand": "ancestors"})
        if r.status_code != 200:
            return {"error": r.status_code}
        d = r.json()
        if not is_allowed(page_id, d.get("ancestors", [])):
            return {"error": "not allowed"}
        r = await c.delete(f"{CONFLUENCE_URL}/rest/api/content/{page_id}/label/{label_name}",
                           headers=get_auth_header())
        if r.status_code not in (200, 204):
            return {"error": r.status_code, "detail": r.text}
        return {"success": True, "id": page_id, "label": label_name}


async def label_list(page_id):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{CONFLUENCE_URL}/rest/api/content/{page_id}", headers=get_auth_header(),
                        params={"expand": "ancestors"})
        if r.status_code != 200:
            return {"error": r.status_code}
        d = r.json()
        if not is_allowed(page_id, d.get("ancestors", [])):
            return {"error": "not allowed"}
        r = await c.get(f"{CONFLUENCE_URL}/rest/api/content/{page_id}/label", headers=get_auth_header())
        if r.status_code != 200:
            return {"error": r.status_code, "detail": r.text}
        labels = [{"name": lb.get("name"), "prefix": lb.get("prefix")} for lb in r.json().get("results", [])]
        return {"id": page_id, "labels": labels, "total": len(labels)}


async def tree(space="NAD"):
    async with httpx.AsyncClient() as c:
        r = await c.get(f"{CONFLUENCE_URL}/rest/api/content", headers=get_auth_header(),
                        params={"spaceKey": space, "limit": 80, "expand": "ancestors"})
        if r.status_code != 200:
            return {"error": r.status_code}
        nodes = {}
        for p in r.json().get("results", []):
            if is_allowed(p.get("id"), p.get("ancestors", [])):
                nodes[p["id"]] = {"title": p["title"], "children": []}
        for p in r.json().get("results", []):
            pid, anc = p["id"], p.get("ancestors", [])
            if pid in nodes and anc and anc[-1]["id"] in nodes:
                nodes[anc[-1]["id"]]["children"].append(pid)
        roots = set(ALLOWED_PAGE_IDS) & set(nodes.keys()) or set(nodes.keys()) - {c for n in nodes.values() for c in n["children"]}
        def fmt(nid, pre="", last=True, d=0):
            if d > 4 or nid not in nodes:
                return ""
            n = nodes[nid]
            s = f"{pre}{'└── ' if last else '├── '}{n['title']}\n"
            cp = pre + ("    " if last else "│   ")
            for i, c in enumerate(n["children"]):
                s += fmt(c, cp, i == len(n["children"]) - 1, d + 1)
            return s
        return {"tree": "".join(fmt(r, "", i == len(roots) - 1) for i, r in enumerate(sorted(roots))).strip()}


def main():
    if not CONFLUENCE_API_TOKEN:
        print(json.dumps({"error": "CONFLUENCE_API_TOKEN not set"}))
        sys.exit(1)
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("search"); s.add_argument("query"); s.add_argument("-s", "--space"); s.add_argument("-l", "--limit", type=int, default=25)
    g = sp.add_parser("get"); g.add_argument("page_id")
    c = sp.add_parser("create"); c.add_argument("-s", "--space", default="NAD"); c.add_argument("-t", "--title", required=True); c.add_argument("-c", "--content", required=True); c.add_argument("-p", "--parent")
    u = sp.add_parser("update"); u.add_argument("page_id"); u.add_argument("-t", "--title"); u.add_argument("-c", "--content")
    sp.add_parser("tree").add_argument("-s", "--space", default="NAD")
    lb = sp.add_parser("label")
    lb_sp = lb.add_subparsers(dest="label_cmd", required=True)
    lb_add = lb_sp.add_parser("add"); lb_add.add_argument("page_id"); lb_add.add_argument("label_name")
    lb_rm = lb_sp.add_parser("remove"); lb_rm.add_argument("page_id"); lb_rm.add_argument("label_name")
    lb_ls = lb_sp.add_parser("list"); lb_ls.add_argument("page_id")
    a = p.parse_args()
    if a.cmd == "search": r = asyncio.run(search(a.query, a.space, a.limit))
    elif a.cmd == "get": r = asyncio.run(get_page(a.page_id))
    elif a.cmd == "create": r = asyncio.run(create(a.space, a.title, a.content, a.parent))
    elif a.cmd == "update": r = asyncio.run(update(a.page_id, a.title, a.content))
    elif a.cmd == "label":
        if a.label_cmd == "add": r = asyncio.run(label_add(a.page_id, a.label_name))
        elif a.label_cmd == "remove": r = asyncio.run(label_remove(a.page_id, a.label_name))
        else: r = asyncio.run(label_list(a.page_id))
    else: r = asyncio.run(tree(a.space))
    print(json.dumps(r, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
