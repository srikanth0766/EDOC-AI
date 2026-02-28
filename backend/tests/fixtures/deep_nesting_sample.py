# Regression fixture: Deep nesting (5 levels)
def deeply_nested(a, b, c, d, e):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        return True
    return False
