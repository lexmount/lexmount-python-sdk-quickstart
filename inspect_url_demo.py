from quickstart_auth import load_environment, prepare_demo

from lexmount import Lexmount

load_environment()


def main() -> None:
    prepare_demo()
    client = Lexmount()

    with client.sessions.create() as session:
        print(f"session_id: {session.id}")
        print(f"inspect_url: {session.inspect_url}")
        input("Press Enter to close the session...")


if __name__ == "__main__":
    main()
