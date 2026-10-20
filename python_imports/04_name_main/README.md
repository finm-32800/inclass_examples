# 04 - `if __name__ == "__main__"`

## What You Learn

- Every module has a variable `__name__`
- When a file is **imported**, `__name__` is the module's name (`"greet"`)
- When a file is **run** (`python greet.py`), `__name__` is `"__main__"`
- Code under `if __name__ == "__main__":` runs only when the file is run,
  never when it is imported

## Files

| File | Purpose |
|------|---------|
| `greet.py` | A module that is also a script: a function, and a `__main__` block that calls it |
| `main.py` | Imports `greet` and calls the function itself |

## How to Run

```bash
cd 04_name_main
python greet.py   # __name__ is '__main__': the block runs
python main.py    # __name__ is 'greet': the block is skipped
```

## Key Concept

The `pull_` modules in the course's repositories end with this block. `dodo.py`
runs `python ./src/pull_fed_funds_futures.py`, so the block runs and pulls the
data. A notebook runs `import pull_fed_funds_futures` and calls its `load_`
function, so the block is skipped and nothing touches the network.

## Try It

- Delete the `if __name__ == "__main__":` line and unindent the call below it.
  Run `python main.py`. How many times does `greet.py` say hello?
- Add `print(__name__)` to the top of `main.py`. What does it print?
