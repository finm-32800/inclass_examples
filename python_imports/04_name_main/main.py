"""Import greet.py as a module.

The top-level print in greet.py runs on import. The block under
`if __name__ == "__main__":` does not, so main.py calls say_hello() itself.
"""

import greet

print("main.py imported greet, and now calls greet.say_hello():")
greet.say_hello()
