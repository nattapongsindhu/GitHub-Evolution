import urllib.request, json, os, datetime

TOKEN = os.environ.get("GITHUB_TOKEN", "")
USER  = "nattapongsindhu"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}

def get(url):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# --- repos ---
repos = []
page = 1
while True:
    data = get(f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}&sort=pushed")
    if not data:
        break
    repos.extend(data)
    if len(data) < 100:
        break
    page += 1

public_repos = [r for r in repos if not r["private"]]
total_stars  = sum(r["stargazers_count"] for r in public_repos)
total_forks  = sum(r["forks_count"] for r in public_repos)

languages = {}
for r in public_repos:
    lang = r.get("language")
    if lang:
        languages[lang] = languages.get(lang, 0) + 1
top_langs = sorted(languages.items(), key=lambda x: -x[1])[:5]

# --- commits last 7 days ---
since = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ")
weekly_commits = 0
active_repos   = []
for r in public_repos[:20]:
    try:
        commits = get(f"https://api.github.com/repos/{USER}/{r['name']}/commits?since={since}&per_page=100")
        count   = len(commits)
        if count > 0:
            weekly_commits += count
            active_repos.append({
                "name":    r["name"],
                "commits": count,
                "pushed":  r["pushed_at"][:10]
            })
    except Exception:
        pass

# --- streak ---
try:
    events    = get(f"https://api.github.com/users/{USER}/events?per_page=100")
    push_days = set()
    for e in events:
        if e["type"] == "PushEvent":
            push_days.add(e["created_at"][:10])
    today  = datetime.date.today()
    streak = 0
    for i in range(30):
        d = (today - datetime.timedelta(days=i)).isoformat()
        if d in push_days:
            streak += 1
        elif i > 0:
            break
except Exception:
    streak = 0

# --- repo index (all public, sorted by last push) ---
repo_index = []
for r in sorted(public_repos, key=lambda x: x.get("pushed_at", ""), reverse=True):
    repo_index.append({
        "name":        r["name"],
        "description": r.get("description") or "",
        "language":    r.get("language") or "",
        "pushed":      r.get("pushed_at", "")[:10]
    })

latest_repo = public_repos[0] if public_repos else {}
now         = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

result = {
    "updated":        now,
    "public_repos":   len(public_repos),
    "total_stars":    total_stars,
    "total_forks":    total_forks,
    "top_languages":  top_langs,
    "weekly_commits": weekly_commits,
    "active_repos":   active_repos[:5],
    "latest_repo":    latest_repo.get("name", ""),
    "latest_pushed":  latest_repo.get("pushed_at", "")[:10],
    "streak_days":    streak,
    "repo_index":     repo_index
}

with open("stats.json", "w") as f:
    json.dump(result, f, indent=2)

print(json.dumps(result, indent=2))
