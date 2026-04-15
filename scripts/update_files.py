import json, datetime, os

with open("stats.json") as f:
    s = json.load(f)

today    = datetime.date.today()
week_num = today.isocalendar()[1]
month    = today.strftime("%B %Y")
year     = today.year

# language list
lang_lines = "\n".join(f"- {l}: {c} repo{'s' if c > 1 else ''}" for l, c in s["top_languages"])

# active repos table
if s["active_repos"]:
    rows = []
    for r in s["active_repos"]:
        rows.append(f"| [{r['name']}](https://github.com/nattapongsindhu/{r['name']}) | {r['commits']} | {r['pushed']} |")
    repo_table = "| Repository | Commits (7d) | Last Push |\n"
    repo_table += "|------------|-------------|----------|\n"
    repo_table += "\n".join(rows)
else:
    repo_table = "_No pushes in the last 7 days_"

# repo index table — auto from API
index_rows = []
for r in s.get("repo_index", []):
    name = r["name"]
    desc = r["description"] if r["description"] else "—"
    lang = r["language"] if r["language"] else "—"
    pushed = r["pushed"]
    index_rows.append(
        f"| [{name}](https://github.com/nattapongsindhu/{name}) | {desc} | {lang} | {pushed} |"
    )

repo_index_table = "| Repo | Description | Language | Last Push |\n"
repo_index_table += "|------|-------------|----------|-----------|\n"
repo_index_table += "\n".join(index_rows) if index_rows else "| — | — | — | — |"

streak_emoji  = "🔥" if s["streak_days"] >= 3 else "📅"
updated_badge = s["updated"].replace(" ", "_").replace(":", "%3A")

readme_parts = [
    "# 🧬 GitHub Evolution\n",
    f"![Last Update](https://img.shields.io/badge/Updated-{updated_badge}-blue?style=flat-square)",
    f"![Repos](https://img.shields.io/badge/Public_Repos-{s['public_repos']}-informational?style=flat-square)",
    f"![Stars](https://img.shields.io/badge/Total_Stars-{s['total_stars']}-yellow?style=flat-square)",
    f"![Weekly](https://img.shields.io/badge/Commits_This_Week-{s['weekly_commits']}-brightgreen?style=flat-square)\n",
    "> Tracking my GitHub development progress, goals, and milestones.",
    "> Auto-updated daily via GitHub Actions.\n",
    "---\n",
    f"## 📊 Live Stats — Week {week_num}, {month}\n",
    "| Metric | Value |",
    "|--------|-------|",
    f"| 📁 Public Repositories | {s['public_repos']} |",
    f"| ⭐ Total Stars | {s['total_stars']} |",
    f"| 🍴 Total Forks | {s['total_forks']} |",
    f"| 📝 Commits This Week | {s['weekly_commits']} |",
    f"| {streak_emoji} Current Streak | {s['streak_days']} day{'s' if s['streak_days'] != 1 else ''} |",
    f"| 🚀 Last Active Repo | [{s['latest_repo']}](https://github.com/nattapongsindhu/{s['latest_repo']}) |",
    f"| 🕐 Last Push | {s['latest_pushed']} |\n",
    "---\n",
    "## 🔥 Active This Week\n",
    repo_table + "\n",
    "---\n",
    "## 💻 Top Languages\n",
    lang_lines + "\n",
    "---\n",
    "## 🗂 All Repositories\n",
    repo_index_table + "\n",
    "---\n",
    f"## 🎯 {year} Goals\n",
    "| Area | Goal | Status |",
    "|------|------|--------|",
    "| IT | Complete Cybersecurity coursework at LACC | 🔄 In progress |",
    "| Aviation | Private Pilot License — bush flying focus | 🔄 In progress |",
    "| GitHub | Maintain consistent commit activity | ✅ Active |",
    "| Career | Build IT portfolio for second income stream | 🔄 In progress |\n",
    "---\n",
    f"_Stats auto-generated from GitHub API · Last run: {s['updated']}_\n"
]

with open("README.md", "w") as f:
    f.write("\n".join(readme_parts))

print("README updated")

# --- monthly log ---
month_fn = f"log/{today.year}/{today.month:02d}-{today.strftime('%B').lower()}.md"
os.makedirs(os.path.dirname(month_fn), exist_ok=True)

if os.path.exists(month_fn):
    with open(month_fn) as f:
        content = f.read()
else:
    content = f"# Log — {today.strftime('%B %Y')}\n\n"

date_str  = today.isoformat()
new_entry = (
    f"\n## {date_str}\n"
    f"- Commits this week: {s['weekly_commits']} "
    f"| Active repos: {len(s['active_repos'])} "
    f"| Streak: {s['streak_days']}d\n"
    f"- Last push: [{s['latest_repo']}](https://github.com/nattapongsindhu/{s['latest_repo']})\n"
)

if date_str not in content:
    content += new_entry
    with open(month_fn, "w") as f:
        f.write(content)
    print(f"Log entry added: {date_str}")
else:
    print(f"Log entry already exists: {date_str}")
