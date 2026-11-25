import json

with open("c:/Users/Admin/Desktop/Composio/composio-app-research/data/pass2_verified.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("--- TARGET APPS CHECK ---")
for r in data:
    if r["id"] in (16, 23, 33, 73, 77, 91):
        print(f"#{r['id']} {r['app_name']}: auth={r['auth_methods']}, url={r['evidence_url']}")

print("\n--- APPENDED URLS CHECK ---")
appended = [r for r in data if "/reference/authentication" in r["evidence_url"] or "/authentication/authentication" in r["evidence_url"]]
print(f"Total appended URLs: {len(appended)}")
for r in appended:
    print(f"#{r['id']} {r['app_name']}: {r['evidence_url']}")

print("\n--- NONE/CLI CHECK ---")
cli_apps = [r for r in data if "None/CLI" in r["auth_methods"]]
for r in cli_apps:
    print(f"#{r['id']} {r['app_name']}: auth={r['auth_methods']}, verdict={r['buildability_verdict']}")
