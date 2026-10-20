"""A module that is also a script.

Run it directly (`python greet.py`) and the block at the bottom runs. Import it
(`import greet`, as main.py does) and the block is skipped.
"""

print(f"Loading greet.py; __name__ is {__name__!r}")


def say_hello():
    print("Hello from greet!")


if __name__ == "__main__":
    # Runs only when this file is the one you ran: python greet.py
    say_hello()
