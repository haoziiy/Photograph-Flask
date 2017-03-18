# coding=utf-8

def log(level, *args, **kwargs):
    def inner(func):
        '''
        * 无名字参数
        ** 有名字参数
        '''
        def warpper(*args, **kwargs):
            print level, 'before calling', func.__name__
            print level, 'args', args
            print level, 'kwargs', kwargs
            func(*args, **kwargs)
            print 'end calling', func.__name__
        return warpper
    return inner

@log(level = 'INFO')
def hello(name, age):
    print 'hello', name, age

if __name__ == '__main__':
    # hello('haoziiy', 15)
    hello(name='haoziiy', age=15)