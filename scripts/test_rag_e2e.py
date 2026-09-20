"""End-to-end RAG test: login, field, upload, advisory, poll citations."""
import sys, time, uuid

sys.path.insert(0, "D:/Sahaayak/sahaayak-project/scripts")
from test_rag_e2e_helpers import q, mpart  # noqa: E402

BASE = "http://127.0.0.1:8001/api/v1"
IMAGE = "D:/Sahaayak/sahaayak-project/frontend/build/images/wheat-hero.jpg"
PHONE = "+919999999999"


def main():
    ok = True

    # 1. Demo login (demo_mode=true)
    r = q("POST", BASE + "/auth/demo", {"role": "farmer"})
    tok = r.get("access_token") or r.get("token")
    assert tok, "no token: %s" % r
    auth = {"Authorization": "Bearer " + tok}
    print("[1] login OK")

    # 2. Field
    fields = q("GET", BASE + "/fields", headers=auth)
    assert isinstance(fields, list) and fields, "no fields: %s" % fields
    field = fields[0]
    print("[2] field OK", field["id"], field.get("crop"))

    # 3. Upload image
    body, hd = mpart(open(IMAGE, "rb").read(), "wheat.jpg")
    up = q("POST", BASE + "/uploads", raw_body=body, headers=hd | auth)
    up_id = up.get("id") or up.get("upload_id")
    assert up_id, "upload failed: %s" % up
    print("[3] upload OK", up_id)

    # 4. Create advisory (idempotent retry check)
    key = uuid.uuid4().hex
    payload = {"field_id": field["id"], "query": "brown spots on wheat leaves",
               "input_type": "image", "upload_ids": [up_id],
               "language": "en", "idempotency_key": key}
    c1 = q("POST", BASE + "/advisories", payload, headers=auth)
    assert c1.get("advisory_id"), "create failed: %s" % c1
    c2 = q("POST", BASE + "/advisories", payload, headers=auth)
    idem = c2.get("advisory_id") == c1["advisory_id"]
    print("[4] advisory OK", c1["advisory_id"], "idempotent:", idem)
    ok = ok and idem

    # 5. Poll for RAG-backed content
    adv = {}
    for _ in range(20):
        time.sleep(2)
        adv = q("GET", BASE + "/advisories/" + c1["advisory_id"], headers=auth)
        if adv.get("detections"):
            break
    det = adv.get("detections") or {}
    rag = det.get("rag") or {}
    cites = adv.get("citations") or []
    if rag:
        print("[5] RAG OK matched=%s disease=%s type=%s" %
              (rag.get("matched"), rag.get("disease"), rag.get("disease_type")))
        print("    symptoms=%s mgmt=%s prevention=%s" %
              (len(rag.get("symptoms") or []), len(rag.get("management") or []),
               len(rag.get("prevention") or [])))
        print("    sources:", rag.get("sources"))
    else:
        print("[5] no det.rag; status=%s disease=%s conf=%s citations=%s" %
              (det.get("status"), det.get("disease"), det.get("confidence"), cites))
        ok = False

    print("RESULT:", "PASS" if ok else "FAIL")


if __name__ == "__main__":
    main()