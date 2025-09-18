from login import login
from requests import Session


def get_db_dump(output_file, session=None):
    if not session:
        session = Session()

    login(session)

    # Fetch the database dump
    response = session.get("http://localhost:8000/db/dump/snapshot/")
    response.raise_for_status()

    # Save the dump to the specified output file
    with open(output_file, "wb") as f:
        f.write(response.content)

    print("Database dump saved to:", output_file)


if __name__ == "__main__":
    get_db_dump("./test/data/dump_test.ih")