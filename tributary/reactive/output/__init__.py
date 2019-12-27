import asyncio
import types
from pprint import pprint
from IPython.display import display

from ..base import _wrap, FunctionWrapper
from .file import File as FileSink  # noqa: F401
from .http import HTTP as HTTPSink  # noqa: F401
from .kafka import Kafka as KafkaSink  # noqa: F401
from .ws import WebSocket as WebSocketSink  # noqa: F401


def Print(foo, foo_kwargs=None):
    foo_kwargs = foo_kwargs or {}
    foo = _wrap(foo, foo_kwargs)

    async def _print(foo):
        async for r in foo():
            if isinstance(r, types.AsyncGeneratorType):
                async for x in r:
                    yield x
            elif isinstance(r, types.CoroutineType):
                yield await r
            else:
                yield r

    return _wrap(_print, dict(foo=foo), name='Print', wraps=(foo,), share=foo)


def Graph(f_wrap):
    if not isinstance(f_wrap, FunctionWrapper):
        raise Exception('ViewGraph expects tributary')
    return f_wrap.view(0)[0]


def PPrint(f_wrap):
    pprint(Graph(f_wrap))


def GraphViz(f_wrap, name='Graph'):
    d = Graph(f_wrap)

    from graphviz import Digraph
    dot = Digraph(name, strict=True)
    dot.format = 'png'

    def rec(nodes, parent):
        for d in nodes:
            if not isinstance(d, dict):
                dot.node(d)
                dot.edge(d, parent)

            else:
                for k in d:
                    dot.node(k)
                    rec(d[k], k)
                    dot.edge(k, parent)

    for k in d:
        dot.node(k)
        rec(d[k], k)

    return dot


def Perspective(foo, foo_kwargs=None, **psp_kwargs):
    foo = _wrap(foo, foo_kwargs or {})

    from perspective import PerspectiveWidget
    p = PerspectiveWidget(psp_kwargs.pop('schema', []), **psp_kwargs)

    async def _perspective(foo):
        async for r in foo():
            if isinstance(r, dict):
                r = [r]
            p.update(r)
            # let PSP render
            await asyncio.sleep(.1)
            yield r

    display(p)

    return _wrap(_perspective, dict(foo=foo), name='Perspective', wraps=(foo,), share=foo)
