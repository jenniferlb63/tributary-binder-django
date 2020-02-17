import time
import tributary.streaming as ts


def foo():
    yield 1
    yield 2


def foo2():
    yield [1, 2]
    yield [3, 4]


class TestUtils:
    def test_delay(self):
        out = ts.Delay(ts.Foo(foo), delay=5)
        now = time.time()
        ret = ts.run(out)
        assert time.time() - now > 5
        assert ret == [1, 2]

    def test_apply(self):
        def square(val):
            return val ** 2

        assert ts.run(ts.Apply(ts.Foo(foo), foo=square)) == [1, 4]

    def test_window_any_size(self):
        assert ts.run(ts.Window(ts.Foo(foo))) == [[1], [1, 2]]

    def test_window_fixed_size(self):
        assert ts.run(ts.Window(ts.Foo(foo), size=2)) == [[1], [1, 2]]

    def test_window_fixed_size_full_only(self):
        assert ts.run(ts.Window(ts.Foo(foo), size=2, full_only=True)) == [[1, 2]]

    # def test_unroll(self):
    #     assert ts.run(ts.Unroll(ts.Foo(foo2))) == [1, 2, 3, 4]

