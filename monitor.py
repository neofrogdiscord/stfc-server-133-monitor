import os
import socket
import ssl
import time
import urllib.request
import json

HOST = "cdn-live-eu1-gwc.startrek.digitgaming.com"
PORT = 443
WEBHOOK = os.environ["DISCORD_WEBHOOK"]

TIMEOUT = 10
ATTEMPTS = 3


def check_server():
    results = []

    try:
        addresses = socket.getaddrinfo(
            HOST,
            PORT,
            type=socket.SOCK_STREAM
        )

        ips = list(dict.fromkeys(
            address[4][0] for address in addresses
        ))

    except Exception as e:
        return False, f"DNS failure: {e}"

    for ip in ips:
        try:
            start = time.time()

            sock = socket.create_connection(
                (ip, PORT),
                timeout=TIMEOUT
            )

            context = ssl.create_default_context()

            tls_sock = context.wrap_socket(
                sock,
                server_hostname=HOST
            )

            latency = round((time.time() - start) * 1000)

            tls_sock.close()

            results.append(
                f"{ip}: OK ({latency} ms)"
            )

        except Exception as e:
            results.append(
                f"{ip}: FAILED ({e})"
            )

    return bool(results) and any(
        "OK" in result for result in results
    ), "\n".join(results)


def send_discord(message):
    data = json.dumps({
        "content": message
    }).encode("utf-8")

    request = urllib.request.Request(
        WEBHOOK,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        return response.status


def main():
    successful = 0
    details = []

    for attempt in range(ATTEMPTS):
        online, result = check_server()

        if online:
            successful += 1

        details.append(
            f"Attempt {attempt + 1}: {'ONLINE' if online else 'OFFLINE'}\n{result}"
        )

        if attempt < ATTEMPTS - 1:
            time.sleep(2)

    if successful == ATTEMPTS:
        status = "🟢 STFC Server 133 monitor: ONLINE"
    elif successful == 0:
        status = "🔴 STFC Server 133 monitor: OFFLINE"
    else:
        status = "🟠 STFC Server 133 monitor: UNCERTAIN"

    message = status + "\n\n" + "\n\n".join(details)

    send_discord(message)


if __name__ == "__main__":
    main()
