import functools
import time

def profile_for_single_function(input):
    all_time = 0
    @functools.wraps(input)
    def func_with_timer(*args, **kwargs):
        if getattr(input, 'status', None):
            print(input.class_name + '.' + input.__name__ + ' started')
        else:
            print(input.__name__ + ' started')
        start = time.time()
        result = input(*args, **kwargs)
        stop = time.time()
        nonlocal all_time
        all_time += (stop - start)
        if getattr(input, 'status', None):
            print(input.class_name + '.' + input.__name__ + ' finished in {0}s'.format(round(all_time, 3)))
        else:
            print(input.__name__ + ' finished in {0}s'.format(round(all_time, 3)))
        return result
    return func_with_timer

def profile(input):
    if isinstance(input, type):
        for attr_name in dir(input):
            if not attr_name.startswith('__') or attr_name == '__init__':
                attr = getattr(input, attr_name)
                attr.status = True
                attr.class_name = input.__name__
                setattr(input, attr_name, profile(attr))
        return input

    return profile_for_single_function(input)


@profile
def qoo(*args, **kwargs):
    time.sleep(0.5)

@profile
class Boo:
    def __init__(self):
        time.sleep(0.5)

    def foo(self):
        time.sleep(0.001)

    def koo(self):
        time.sleep(0.001)


if __name__ == '__main__':
    b = Boo()
    b.foo()
    qoo()
    b.koo()
    qoo()
    qoo()
    qoo()
    c = Boo()
    qoo()
