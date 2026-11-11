import json, sys, time, urllib.request, uuid, os, re
from pathlib import Path
ENV = Path("/Users/zarko.stefanov/Kivi's/.env").read_text()
KEY = re.search(r"([A-Za-z0-9]{24,})", ENV).group(1)
SRC = Path("/Users/zarko.stefanov/Kivi's/website/assets-src/images")
OUT = Path("/Users/zarko.stefanov/Kivi's/Images/Enhanced")
H = {"Authorization": f"Bearer {KEY}"}

BASE = ("Professional photo retouch of THIS EXACT photograph for a premium restaurant website. "
 "Keep the scene 100% identical: same place, same architecture, furniture, objects, food, cups, plates, packaging, signage, logos, lettering, "
 "plants, people/hands, their positions and the camera framing. Do NOT add, remove, move, replace or redesign anything, do not invent new details, "
 "do not change any text or logo. Only improve the photography itself: bright, warm, sunny and welcoming mood; soft natural daylight with a gentle "
 "warm sun glow; lifted shadows; clean neutral whites; correct white balance and exposure; rich but true-to-life colors; natural, appetizing food colors; "
 "crisp detail and sharpness; remove noise, haze and color casts; subtle professional contrast, like an editorial interior and food photograph shot on a "
 "full-frame camera with a quality lens. Photorealistic. No text overlays, no watermark, no borders, no filters, no illustration or CGI look.")
JOBS = [
 ("hero",           "4:3", "Interior of a cafe bar with a dark green wall, a large white kiwi bird line logo, hanging Edison bulbs and a brick-front counter. Make the bulbs glow softly warm and fill the room with gentle daylight so the green wall and wood look rich and inviting; keep the brick counter lettering exactly as is."),
 ("nest-interior",  "3:4", "Bright cafe interior with wooden tables and chairs and a glass front. Let warm late-morning sunlight come in through the glass front, soft light on the floor and tables, airy and cosy."),
 ("nest-terrace",   "4:3", "Garden terrace of the cafe on a clear sunny afternoon: deep blue sky, lush fresh-green lawn, warm sunlight on the building wall, soft shadows of the furniture."),
 ("nest-exterior",  "4:3", "Street view of the cafe entrance. Additionally correct the camera perspective: straighten converging verticals so all building walls and door frames are perfectly vertical and level the horizon, as if shot with a tilt-shift lens at eye level, while keeping the whole entrance, sign and terrace in frame (only a minimal crop if needed). Clear blue sky, warm sunlight on the facade."),
 ("nest-portion",   "3:4", "A hand holding a protein bowl plate in front of the green wall with the kiwi logo. Make the food look fresh and appetizing with natural vibrant colors; soft warm light on the plate; keep background as is but slightly brighter."),
 ("nest-sandwich",  "3:4", "A hand holding a brioche sandwich in front of the cafe glass entrance. Fresh appetizing food colors, bright sunny daylight, clean reflections."),
 ("nest-door",      "3:4", "A hand holding a protein bowl plate in front of the cafe entrance with the KiWi'S sign on the glass. Fresh appetizing food colors, bright sunny daylight."),
 ("nest-dessert",   "3:4", "A hand holding a protein dessert jar with the kiwi label in front of the green wall. Crisp dessert layers, warm soft light, background slightly brighter but unchanged."),
 ("nest-frappe",    "3:4", "An iced coffee with cream foam and biscuit crumble on an outdoor table with greenery behind. Bright sunny summer light, fresh green plants, glistening ice coffee."),
]

def req(url, data=None, headers=None, method=None):
    r = urllib.request.Request(url, data=data, headers={**H, **(headers or {})}, method=method)
    with urllib.request.urlopen(r, timeout=120) as f:
        return json.loads(f.read())

def upload(path):
    b = "----kiwi" + uuid.uuid4().hex
    body = b"".join([
        f"--{b}\r\nContent-Disposition: form-data; name=\"uploadPath\"\r\n\r\nkiwis\r\n".encode(),
        f"--{b}\r\nContent-Disposition: form-data; name=\"fileName\"\r\n\r\n{path.name}\r\n".encode(),
        f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{path.name}\"\r\nContent-Type: image/jpeg\r\n\r\n".encode(),
        path.read_bytes(), f"\r\n--{b}--\r\n".encode()])
    j = req("https://kieai.redpandaai.co/api/file-stream-upload", body, {"Content-Type": f"multipart/form-data; boundary={b}"}, "POST")
    if not j.get("success", j.get("code") == 200): raise RuntimeError(f"upload failed: {j.get('msg')}")
    return j["data"]["downloadUrl"]

tasks = {}
for name, ar, extra in JOBS:
    url = upload(SRC / f"{name}.jpg")
    payload = {"model": "nano-banana-2", "input": {"prompt": BASE + " Scene: " + extra, "image_input": [url], "aspect_ratio": ar, "resolution": "1K", "output_format": "jpg"}}
    j = req("https://api.kie.ai/api/v1/jobs/createTask", json.dumps(payload).encode(), {"Content-Type": "application/json"}, "POST")
    if j.get("code") != 200: print(name, "CREATE FAILED:", j.get("msg"), flush=True); continue
    tasks[name] = j["data"]["taskId"]; print(name, "task created", flush=True)

credits = 0
deadline = time.time() + 1800
while tasks and time.time() < deadline:
    time.sleep(10)
    for name, tid in list(tasks.items()):
        j = req(f"https://api.kie.ai/api/v1/jobs/recordInfo?taskId={tid}")
        d = j.get("data") or {}
        if d.get("state") == "success":
            u = json.loads(d["resultJson"])["resultUrls"][0]
            with urllib.request.urlopen(u, timeout=120) as f: (OUT / f"{name}.jpg").write_bytes(f.read())
            credits += d.get("creditsConsumed") or 0
            print(name, "DONE", flush=True); del tasks[name]
        elif d.get("state") == "fail":
            print(name, "FAILED:", d.get("failMsg"), flush=True); del tasks[name]
print("finished; credits used:", credits, "pending:", list(tasks), flush=True)
