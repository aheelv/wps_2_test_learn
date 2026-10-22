#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通过 GitHub REST API 发布本地站点到已有仓库（保留历史：在 main 现有提交之上新建提交）。
用法：
    python tools/gh_publish.py --dry-run   # 只打印差异，不写远端
    python tools/gh_publish.py --apply     # 实际创建 blob / tree / commit 并更新 ref
"""
import base64
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

OWNER = "aheelv"
REPO = "wps_2_test_learn"
BRANCH = "main"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://api.github.com"

EXCLUDE_DIRS = {".git", ".workbuddy", "_build", ".trae-html-share-packages"}
EXCLUDE_FILES = {"Thumbs.db", "desktop.ini", ".DS_Store"}
EXCLUDE_PREFIX = (".tmp_", ".t_", ".chk_", ".p2.")


def token():
    p = os.path.expanduser("~/.git-credentials")
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if line.startswith("https://") and "@github.com" in line:
            body = line[len("https://"):-len("@github.com")]
            if ":" in body:
                return body.split(":", 1)[1]
    raise SystemExit("未找到 GitHub 凭据")


TOK = token()


def api(path, method="GET", payload=None, raw=False):
    url = path if path.startswith("http") else API + path
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", "Bearer " + TOK)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if data:
        req.add_header("Content-Type", "application/json; charset=utf-8")
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                body = r.read()
                return body if raw else json.loads(body.decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:400]
            if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            raise SystemExit("API %s %s -> %s %s" % (method, path, e.code, detail))
        except Exception:
            if attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            raise
    raise SystemExit("API 重试失败: " + path)


def local_files():
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if fn in EXCLUDE_FILES or fn.startswith(EXCLUDE_PREFIX):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ROOT).replace("\\", "/")
            out.append(rel)
    return sorted(out)


def blob_sha(data):
    h = hashlib.sha1()
    h.update(b"blob %d\x00" % len(data))
    h.update(data)
    return h.hexdigest()


def main():
    apply = "--apply" in sys.argv

    ref = api("/repos/%s/%s/git/ref/heads/%s" % (OWNER, REPO, BRANCH))
    head_sha = ref["object"]["sha"]
    commit = api("/repos/%s/%s/git/commits/%s" % (OWNER, REPO, head_sha))
    base_tree = commit["tree"]["sha"]
    print("远端 HEAD  :", head_sha)
    print("远端 tree  :", base_tree)
    print("HEAD 提交  :", commit["message"].splitlines()[0][:70])

    tree = api("/repos/%s/%s/git/trees/%s?recursive=1" % (OWNER, REPO, base_tree))
    remote = {e["path"]: e for e in tree["tree"] if e["type"] == "blob"}
    print("远端文件数 :", len(remote), "(truncated=%s)" % tree.get("truncated"))

    locals_ = local_files()
    print("本地文件数 :", len(locals_))

    add, same = [], []
    for rel in locals_:
        data = open(os.path.join(ROOT, rel.replace("/", os.sep)), "rb").read()
        sha = blob_sha(data)
        if rel in remote and remote[rel]["sha"] == sha:
            same.append(rel)
        else:
            add.append((rel, data, sha, rel in remote))
    remote_only = sorted(set(remote) - set(locals_))

    new_files = [a for a in add if not a[3]]
    mod_files = [a for a in add if a[3]]
    print()
    print("新增 %d 个 / 修改 %d 个 / 未变 %d 个" % (len(new_files), len(mod_files), len(same)))
    if new_files:
        print("--- 新增 ---")
        for rel, d, s, _ in new_files:
            print("  + %-40s %8d B" % (rel, len(d)))
    if mod_files:
        print("--- 修改 ---")
        for rel, d, s, _ in mod_files:
            print("  M %-40s %8d B" % (rel, len(d)))
    if remote_only:
        print("--- 仅远端存在（本次不删除，以免丢失历史内容）%d 个 ---" % len(remote_only))
        for rel in remote_only[:40]:
            print("  ? " + rel)
        if len(remote_only) > 40:
            print("  ... 其余 %d 个" % (len(remote_only) - 40))

    if not apply:
        print("\n[dry-run] 未写入远端。")
        return
    if not add:
        print("\n无差异，无需提交。")
        return

    entries = []
    for i, (rel, data, sha, _) in enumerate(add, 1):
        blob = api("/repos/%s/%s/git/blobs" % (OWNER, REPO), "POST", {
            "content": base64.b64encode(data).decode("ascii"),
            "encoding": "base64",
        })
        entries.append({"path": rel, "mode": "100644", "type": "blob", "sha": blob["sha"]})
        print("  [%d/%d] blob %s  %s" % (i, len(add), blob["sha"][:8], rel))

    new_tree = api("/repos/%s/%s/git/trees" % (OWNER, REPO), "POST", {
        "base_tree": base_tree,
        "tree": entries,
    })
    print("新 tree    :", new_tree["sha"])

    msg = os.environ.get("GH_COMMIT_MSG") or "更新 WPS 二级实操训练体系：8 次课 / 32 小节 / 72 题"
    new_commit = api("/repos/%s/%s/git/commits" % (OWNER, REPO), "POST", {
        "message": msg,
        "tree": new_tree["sha"],
        "parents": [head_sha],
    })
    print("新 commit  :", new_commit["sha"])

    api("/repos/%s/%s/git/refs/heads/%s" % (OWNER, REPO, BRANCH), "PATCH", {
        "sha": new_commit["sha"], "force": False,
    })
    print("已更新 refs/heads/%s -> %s" % (BRANCH, new_commit["sha"]))
    print("提交页面 : https://github.com/%s/%s/commit/%s" % (OWNER, REPO, new_commit["sha"]))


if __name__ == "__main__":
    main()
