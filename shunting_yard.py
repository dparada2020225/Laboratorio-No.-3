"""
Shunting Yard Algorithm
Laboratorio 3 - Teoría de la Computación

Convierte una expresión regular en notación infix a postfix.
Basado en el pseudocódigo del Laboratorio 2.
"""


def get_precedence(c: str) -> int:
    """Retorna la precedencia del operador c."""
    precedences = {
        '(': 1,
        '|': 2,
        '.': 3,
        '?': 4,
        '*': 4,
        '+': 4,
        '^': 5,
    }
    return precedences.get(c, 0)


def format_regex(regex: str) -> str:
    """
    Agrega operadores explícitos de concatenación ('.') donde corresponda.
    Ejemplo: 'ab' → 'a.b', 'a*b' → 'a*.b'
    """
    all_operators = set('|?+*^')
    binary_operators = set('^|')
    res = ''

    for i in range(len(regex) - 1):
        c1 = regex[i]
        c2 = regex[i + 1]
        res += c1

        if (c1 != '(' and
                c2 != ')' and
                c2 not in all_operators and
                c1 not in binary_operators):
            res += '.'

    # Agregar el último carácter
    if regex:
        res += regex[-1]

    return res


def infix_to_postfix(regex: str) -> tuple[str, str]:
    """
    Convierte una expresión regular infix a postfix usando Shunting Yard.

    Retorna:
        (formatted, postfix) — regex con concatenación explícita y notación postfix.
    """
    operators = set('*+?.|')
    postfix = ''
    stack: list[str] = []
    formatted = format_regex(regex)

    for c in formatted:
        if c == '(':
            stack.append(c)

        elif c == ')':
            while stack and stack[-1] != '(':
                postfix += stack.pop()
            if stack:
                stack.pop()  # descartar '('

        elif c in operators:
            while (stack and
                   stack[-1] != '(' and
                   get_precedence(stack[-1]) >= get_precedence(c)):
                postfix += stack.pop()
            stack.append(c)

        else:
            # Operando (letra, dígito, ε) → directo a salida
            postfix += c

    while stack:
        postfix += stack.pop()

    return formatted, postfix


if __name__ == '__main__':
    test_cases = [
        '(a*|b*)+',
        '((ε|a)|b*)*',
        '(a|b)*abb(a|b)*',
        '0?(1?)?0*',
    ]
    for regex in test_cases:
        fmt, postfix = infix_to_postfix(regex)
        print(f'Infix:    {regex}')
        print(f'Formated: {fmt}')
        print(f'Postfix:  {postfix}')
        print()
