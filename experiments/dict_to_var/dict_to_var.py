cmd_ctx = {
    "globals": {
        "g_a": 1,
        "g_b": 2,
        "g_c": 3
    },
    "locals": {
        "l_a": 4,
        "l_b": 5,
        "l_c": 6
    }
}

#foo, bar = map(d.get, ('foo', 'bar'))
#a = map(cmd_ctx.get, (cmd_ctx["locals"].keys()))
#print(list(a))

print(f'{locals()=}, {globals()=}')
globals().update((k, v) for k, v in cmd_ctx["locals"].items())

print(f'{l_a=}, {l_b=}, {l_c=}')

l_a = 'hello'
print(f'{locals()=}, {globals()=}, {locals()["l_a"]=}')

#l_a = l_a + 1 ... locals["l_a"] = locals["l_a"] + 1
