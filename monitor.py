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
