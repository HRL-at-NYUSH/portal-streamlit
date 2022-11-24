import json

def get_variable_filter(const_path, oov_path):
    with open(const_path, 'r') as f:
        const = json.load(f)
    with open(oov_path, 'r') as f:
        oov = json.load(f)
    return remove_oov(const, oov)


def remove_oov(const, oov):
    va = {}
    fi = {}
    for graph, varlist in const['variables'].items():
        va[graph] = [v for v in varlist if v not in oov]
    for v, vfilist in const['filters'].items():
        if v in oov:
            continue
        fi[v] = [fv for fv in vfilist if fv not in oov]
    return va, fi
