from  __future__ import annotations
import MainView as MV
class A:
    a=1
    b=2





class B(A):
    c=3

if __name__ == '__main__':
    import inspect
    import sys
    for name, obj in inspect.getmembers(MV):
        if inspect.isclass(obj):
            print(name)
    a_obj = A()
    b_obj = B()
    print('')