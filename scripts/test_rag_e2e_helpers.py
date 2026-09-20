"""Helper: HTTP helpers for the e2e RAG test."""
import json, urllib.request, urllib.error, uuid as _uuid


def q(method, path, body=None, raw_body=None, headers=None, timeout=60):
    hd = {"Content-Type": "application/json", "Accept": "application/json"}
    if headers:
        hd.update(headers)
    data = None
    if raw_body is not None:
        data = raw_body
        if "Content-Type" not in hd:
            hd["Content-Type"] = "application/octet-stream"
    elif body is not None:
        data = json.dumps(body).encode("utf-8")
    r = urllib.request.Request(path, data=data, headers=hd, method=method)
    try:
        with urllib.request.urlopen(r, timeout=timeout) as resp:
            txt = resp.read().decode("utf-8", errors="replace")
            try:
                return json.loads(txt)
            except Exception:
                return {"_raw": txt, "_status": resp.status}
    except urllib.error.HTTPError as e:
        try:
            txt = e.read().decode("utf-8", errors="replace")
        except Exception:
            txt = "<HTTP %d>" % e.code
        return {"_error": True, "code": e.code, "_raw": txt[:300]}
    except Exception as e:
        return {"_error": True, "exc": repr(e)}


def mpart(file_bytes, filename="test.jpg"):
    boundary = "---B" + _uuid.uuid4().hex
    out = b""
    out += ("--" + boundary + "\r\n").encode()
    out += ('Content-Disposition: form-data; name="file"; filename="' + filename + '"\r\n').encode()
    out += b"Content-Type: image/jpeg\r\n\r\n"
    out += file_bytes
    out += ("\r\n--" + boundary + "--\r\n").encode()
    hd = {"Content-Type": "multipart/form-data; boundary=" + boundary,
          "Accept": "application/json"}
    return out, hd
