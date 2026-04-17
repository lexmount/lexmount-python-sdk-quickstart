from dotenv import load_dotenv

from lexmount import Lexmount

load_dotenv(override=True)


def main() -> None:
    client = Lexmount()
    session = client.sessions.create()

    try:
        print(f"session_id: {session.id}")
        print("Listing session targets...")

        targets = client.sessions.list_targets(session.id)
        print(f"Found {len(targets)} targets\n")

        for target in targets:
            print(f"target_id: {target.id}")
            print(f"title: {target.title}")
            print(f"type: {target.type}")
            print(f"url: {target.url}")
            print(f"inspectUrl: {target.inspectUrl or 'N/A'}")
            print(
                "webSocketDebuggerUrl: "
                f"{target.webSocketDebuggerUrlTransformed or target.webSocketDebuggerUrl or 'N/A'}"
            )
            print()
        input("Press Enter to continue...")
    finally:
        client.sessions.delete(session_id=session.id)
        client.close()


if __name__ == "__main__":
    main()
