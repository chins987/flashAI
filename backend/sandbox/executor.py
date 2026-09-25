
"""Safe, deterministic arithmetic evaluator. No eval/exec and no arbitrary code execution."""
import ast, operator as op

BIN = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
       ast.FloorDiv: op.floordiv, ast.Mod: op.mod, ast.Pow: op.pow}
UN = {ast.UAdd: op.pos, ast.USub: op.neg}

def arithmetic(expression: str):
    tree = ast.parse(expression, mode="eval")
    def walk(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int,float)) and not isinstance(n.value,bool):
            return n.value
        if isinstance(n, ast.UnaryOp) and type(n.op) in UN:
            return UN[type(n.op)](walk(n.operand))
        if isinstance(n, ast.BinOp) and type(n.op) in BIN:
            a,b=walk(n.left),walk(n.right)
            if type(n.op) is ast.Pow and abs(b)>100: raise ValueError("Exponent too large")
            return BIN[type(n.op)](a,b)
        raise ValueError("Only numeric arithmetic expressions are allowed")
    return walk(tree.body)
