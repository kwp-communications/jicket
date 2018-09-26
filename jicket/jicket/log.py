"""Helper functions for logging"""

def info(msg: str) -> None:
    print("\33[1m\33[34mInfo:\33[0m %s" % msg)

def success(msg: str) -> None:
    print("\33[1m\33[32mSuccess:\33[0m %s" % msg)

def warning(msg: str) -> None:
    print("\33[1m\33[33mWarning:\33[0m %s" % msg)

def error(msg: str) -> None:
    print("\33[1m\33[31mError:\33[0m %s" % msg)
