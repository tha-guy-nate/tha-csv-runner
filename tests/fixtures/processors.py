def noop(row: dict) -> None:
    pass


def fail_on_bob(row: dict) -> None:
    if row["name"] == "Bob":
        raise ValueError("Bob is not allowed")
