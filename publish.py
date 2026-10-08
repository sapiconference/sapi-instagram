"""Automatické zverejňovanie SAPI carouselov na Instagram (Instagram API s prihlásením cez Instagram)."""
import json, os, sys, time, datetime
from zoneinfo import ZoneInfo
import requests

API = "https://graph.instagram.com/v23.0"
TOKEN = os.environ.get("IG_TOKEN", "").strip()
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"
REPO = os.environ.get("GITHUB_REPOSITORY", "")
BRANCH = os.environ.get("GITHUB_REF_NAME", "main")
BASE_URL = os.environ.get("IMAGE_BASE_URL") or f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/images"


def api(method, path, **params):
    params["access_token"] = TOKEN
    r = requests.request(method, f"{API}/{path}", params=params, timeout=60)
    data = r.json() if r.content else {}
    if r.status_code >= 400 or "error" in data:
        raise RuntimeError(f"{method} {path} → {r.status_code}: {data}")
    return data


def wait_ready(container_id, tries=30):
    for _ in range(tries):
        st = api("GET", container_id, fields="status_code").get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Kontajner {container_id} skončil so stavom {st}")
        time.sleep(5)
    raise RuntimeError(f"Kontajner {container_id} nie je pripravený ani po čakaní")


def create_item(ig_id, url, alt):
    try:
        return api("POST", f"{ig_id}/media", image_url=url, is_carousel_item="true", alt_text=alt)["id"]
    except RuntimeError as e:
        if "alt_text" in str(e):
            print("  alt_text nebol prijatý, skúšam bez neho")
            return api("POST", f"{ig_id}/media", image_url=url, is_carousel_item="true")["id"]
        raise


def publish(ig_id, post):
    children = []
    for i in range(1, 6):
        url = f"{BASE_URL}/{post['priecinok']}/{i}.jpg"
        cid = create_item(ig_id, url, post["alt_texty"][i - 1])
        wait_ready(cid)
        children.append(cid)
        print(f"  obrázok {i}/5 pripravený")
    container = api("POST", f"{ig_id}/media", media_type="CAROUSEL",
                    children=",".join(children), caption=post["popisok"])["id"]
    wait_ready(container)
    return api("POST", f"{ig_id}/media_publish", creation_id=container)["id"]


def check_images(post):
    for i in range(1, 6):
        url = f"{BASE_URL}/{post['priecinok']}/{i}.jpg"
        r = requests.head(url, timeout=30, allow_redirects=True)
        ok = r.status_code == 200 and r.headers.get("content-type", "").startswith("image/jpeg")
        print(f"  {'OK ' if ok else 'CHYBA'} {url} ({r.status_code}, {r.headers.get('content-type')})")
        if not ok:
            return False
    return True


def main():
    plan = json.load(open("harmonogram.json", encoding="utf-8"))
    state = json.load(open("zverejnene.json", encoding="utf-8"))
    tz = ZoneInfo(plan["casova_zona"])
    now = datetime.datetime.now(tz)

    due = [p for p in plan["prispevky"]
           if str(p["poradie"]) not in state["zverejnene"]
           and datetime.datetime.fromisoformat(f"{p['datum']}T{p['cas']}").replace(tzinfo=tz) <= now]

    if DRY_RUN:
        print("TESTOVACÍ BEH – nič sa nezverejní.")
        me = api("GET", "me", fields="user_id,username")
        print(f"Token funguje, účet: @{me.get('username')} (id {me.get('user_id')})")
        nxt = next((p for p in plan["prispevky"] if str(p["poradie"]) not in state["zverejnene"]), None)
        if nxt:
            print(f"Najbližší príspevok: #{nxt['poradie']} {nxt['tema']} – {nxt['datum']} {nxt['cas']}")
            ok = check_images(nxt)
            print("Obrázky sú dostupné." if ok else "Obrázky NIE SÚ dostupné – skontroluj, či je repozitár verejný.")
            sys.exit(0 if ok else 1)
        return

    if not due:
        print(f"{now:%Y-%m-%d %H:%M} – nič na zverejnenie.")
        return

    me = api("GET", "me", fields="user_id,username")
    ig_id = me["user_id"]
    post = due[0]  # najviac jeden carousel na jeden beh
    print(f"Zverejňujem #{post['poradie']} {post['tema']} na @{me.get('username')}")
    media_id = publish(ig_id, post)
    state["zverejnene"][str(post["poradie"])] = {"media_id": media_id, "cas": now.isoformat(timespec="minutes")}
    json.dump(state, open("zverejnene.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"Hotovo, media id {media_id}")


if __name__ == "__main__":
    if not TOKEN:
        sys.exit("Chýba IG_TOKEN (GitHub Secret).")
    main()
