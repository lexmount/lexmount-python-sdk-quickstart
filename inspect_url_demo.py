from dotenv import load_dotenv

from lexmount import Lexmount

load_dotenv(override=True)


def main() -> None:
    client = Lexmount()

    with client.sessions.create() as session:
        print(f"session_id: {session.id}")
        print(f"inspect_url: {session.inspect_url}")
        input("Press Enter to close the session...")


if __name__ == "__main__":
    main()
