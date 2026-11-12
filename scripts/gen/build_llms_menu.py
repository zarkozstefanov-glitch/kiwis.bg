"""Rewrites the '## Меню' block of llms.txt from menu_data.json (run from website/)."""
import json
d = {c["id"]: c for c in json.load(open("scripts/gen/menu_data.json"))}
def e(p):
    s = p.replace(".00", "").replace(".", ",")
    if "," in s and len(s.split(",")[1]) == 1: s += "0"
    return s + " €"
low = lambda s: s[0].lower() + s[1:] if not s.startswith("Black") else s
L = ["## Меню", "", "### Cloud Foam и матча"]
L += [f"- {i['bg']} – {e(i['price'])}: {low(i['dbg'])}" for i in d["cloud"]["items"]]
L += ["", "### Протеинови сандвичи (протеинов бриош)"]
L += [f"- {i['bg'].replace(' Бриош', ' бриош')}, {i['w']} – {e(i['price'])}: {low(i['dbg'])}" for i in d["sandwich"]["items"]]
L += ["", "### Протеинови порции (с басмати ориз)"]
L += [f"- {i['bg']}, {i['w']} – {e(i['price'])}: {low(i['dbg'])}" for i in d["portion"]["items"]]
L += ["", "### Салати"]
L += [f"- {i['bg']}, {i['w']} – {e(i['price'])}: {low(i['dbg'])}" for i in d["salad"]["items"]]
L += ["", "### Протеинови десерти в кен (250 г, 5 € всеки)"]
L += [f"- {i['bg']}: {low(i['dbg'])}" for i in d["dessert"]["items"]]
rows = d["coffee"]["rows"]
L += ["", "### Кафе и напитки"] + ["- " + "; ".join(f"{r[1].lower() if j else r[1]} – {e(r[2])}" for j, r in enumerate(rows[k:k + 4])) for k in range(0, len(rows), 4)]
t = open("llms.txt").read()
a, b = t.index("## Меню"), t.index("## Вегетариански опции")
open("llms.txt", "w").write(t[:a] + "\n".join(L) + "\n\n" + t[b:])
print("llms.txt menu updated")
