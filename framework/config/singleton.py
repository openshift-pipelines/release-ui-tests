from typing import Dict, TypeVar

T = TypeVar("T")


class Singleton(type):
    """
    Singleton class - Not thread safe
    The Singleton Pattern - ensuring that a class can only be used to create a single instance and providing a single
    global access point.
    Allows us to access the same object in multiple points of our programs without the fear that it may be overwritten
    at some point in our program.
    https://stackabuse.com/the-singleton-design-pattern-in-python/
    """

    _instances = {}

    def __call__(cls, *args: object, **kwargs: Dict[str, object]) -> object:
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
