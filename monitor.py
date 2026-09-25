import os
import urllib.request
import json

webhook = os.environ["DISCORD_WEBHOOK"]

data = json.dumps({
    "content": "✅ STFC monitor Discord test successful!"
}).encode("utf-8")

request = urllib.request.Request(
    webhook,
    data=data,
    headers={
        "Content-Type": "application/json",
        "User-Agent": "STFC-Server-133-Monitor"
    },
    method="POST"
)

with urllib.request.urlopen(request, timeout=15) as response:
    print("Discord response:", response.status)
