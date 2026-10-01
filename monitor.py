import os
import socket
import ssl
import time
import urllib.request
import urllib.error
import json

HOST = "cdn-live-eu1-web.startrek.digitgaming.com"
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
            family=socket.AF_INET,
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


def test_live_eu1():
    host = "cdn-live-eu1-web.startrek.digitgaming.com"

    print(f"\nTesting {host}")

    try:
        start = time.time()

        request = urllib.request.Request(
            f"https://{host}/",
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "*/*",
                "Accept-Language": "en-GB,en;q=0.9"
            }
        )

        context = ssl.create_default_context()

        with urllib.request.urlopen(
            request,
            timeout=TIMEOUT,
            context=context
        ) as response:

            latency = round((time.time() - start) * 1000)

            print(f"HTTP status: {response.status}")
            print(f"Latency: {latency} ms")
            print(
                f"Content-Type: "
                f"{response.headers.get('Content-Type')}"
            )

            print("Response headers:")
            print(response.headers)

            body = response.read(500)

            print("Response:")
            print(
                body.decode(
                    "utf-8",
                    errors="replace"
                )
            )

    except urllib.error.HTTPError as e:
        print(f"HTTP status: {e.code}")

        print("Response headers:")
        print(e.headers)

        try:
            body = e.read(500)

            print("Response:")
            print(
                body.decode(
                    "utf-8",
                    errors="replace"
                )
            )

        except Exception:
            pass

    except Exception as e:
        print(f"TEST FAILED: {e}")


def send_discord(message):
    data = json.dumps({
        "content": message
    }).encode("utf-8")

    request = urllib.request.Request(
        WEBHOOK,
        data=data,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "STFC-Server-133-Monitor/1.0"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:
            print(
                "Discord response:",
                response.status
            )

    except urllib.error.HTTPError as e:
        print(
            "Discord HTTP error:",
            e.code
        )
        print(
            "Discord response:",
            e.read().decode(
                "utf-8",
                errors="replace"
            )
        )
        raise


def main():
    test_live_eu1()

    successful = 0
    details = []

    for attempt in range(ATTEMPTS):
        online, result = check_server()

        if online:
            successful += 1

        details.append(
            f"Attempt {attempt + 1}: "
            f"{'ONLINE' if online else 'OFFLINE'}\n"
            f"{result}"
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
