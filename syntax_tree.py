"""
Árbol Sintáctico para Expresiones Regulares
Laboratorio 3 - Teoría de la Computación

Construye y visualiza el árbol sintáctico a partir de una expresión
regular en notación postfix.

Simplificaciones aplicadas:
    r+  →  r . r*       (uno o más)
    r?  →  r | ε        (cero o uno)
"""

import copy
import matplotlib
matplotlib.use('Agg')          # backend sin ventana (para guardar PNG)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch


# ──────────────────────────────────────────────
# Estructura del nodo
# ──────────────────────────────────────────────

class Node:
    """Nodo del árbol sintáctico."""

    def __init__(self, value: str, left: 'Node | None' = None,
                 right: 'Node | None' = None):
        self.value = value
        self.left = left    # hijo izquierdo (o único hijo en operadores unarios)
        self.right = right  # hijo derecho (None en operadores unarios)

    def __repr__(self) -> str:
        return f'Node({self.value!r})'


# ──────────────────────────────────────────────
# Construcción del árbol desde postfix
# ──────────────────────────────────────────────

BINARY_OPS = frozenset('|.')
UNARY_OPS  = frozenset('*+?')


def build_tree(postfix: str) -> Node | None:
    """
    Construye el árbol sintáctico a partir de una expresión postfix.

    Aplica las simplificaciones:
        '+' → r . r*    (se duplica el subárbol)
        '?' → r | ε
    """
    stack: list[Node] = []

    for c in postfix:
        if c == '*':
            child = stack.pop()
            stack.append(Node('*', child))

        elif c == '+':
            # r+ = r . r*  (simplificación)
            r = stack.pop()
            r_copy = copy.deepcopy(r)
            star_node = Node('*', r_copy)
            stack.append(Node('.', r, star_node))

        elif c == '?':
            # r? = r | ε  (simplificación)
            r = stack.pop()
            stack.append(Node('|', r, Node('ε')))

        elif c in BINARY_OPS:
            right = stack.pop()
            left  = stack.pop()
            stack.append(Node(c, left, right))

        else:
            # Operando (símbolo o ε)
            stack.append(Node(c))

    return stack[0] if stack else None


# ──────────────────────────────────────────────
# Algoritmo de posicionamiento (in-order)
# ──────────────────────────────────────────────

def _assign_positions(node: Node | None, depth: int,
                      pos: dict, counter: list) -> None:
    """
    Asigna coordenadas (x, y) a cada nodo usando recorrido in-order.
    El eje x crece con el contador; el eje y disminuye con la profundidad.
    """
    if node is None:
        return
    _assign_positions(node.left,  depth + 1, pos, counter)
    pos[id(node)] = (counter[0], -depth)
    counter[0] += 1
    _assign_positions(node.right, depth + 1, pos, counter)


def _collect_nodes(node: Node | None, pos: dict,
                   nodes: list) -> None:
    """Recorre el árbol y acumula (node, x, y)."""
    if node is None:
        return
    x, y = pos[id(node)]
    nodes.append((node, x, y))
    _collect_nodes(node.left,  pos, nodes)
    _collect_nodes(node.right, pos, nodes)


# ──────────────────────────────────────────────
# Visualización con matplotlib
# ──────────────────────────────────────────────

OPERATOR_COLOR  = '#4A90D9'   # azul para operadores
OPERAND_COLOR   = '#27AE60'   # verde para operandos
EPSILON_COLOR   = '#E67E22'   # naranja para ε
EDGE_COLOR      = '#555555'
NODE_RADIUS     = 0.35
FONT_SIZE       = 11


def _node_color(value: str) -> str:
    if value in ('*', '+', '?', '|', '.'):
        return OPERATOR_COLOR
    if value == 'ε':
        return EPSILON_COLOR
    return OPERAND_COLOR


def _display_label(value: str) -> str:
    """Etiqueta visible en el nodo (cambia '.' por '∘' para concatenación)."""
    return '∘' if value == '.' else value


def draw_tree(root: Node | None, title: str = 'Árbol Sintáctico',
              filename: str | None = None) -> None:
    """
    Dibuja el árbol sintáctico y lo guarda en `filename` (PNG).
    Si filename es None, usa el título como nombre de archivo.
    """
    if root is None:
        print(f'[ADVERTENCIA] Árbol vacío para: {title}')
        return

    # Calcular posiciones
    pos: dict = {}
    _assign_positions(root, 0, pos, [0])

    # Recolectar nodos
    nodes: list = []
    _collect_nodes(root, pos, nodes)

    if not nodes:
        return

    xs = [x for _, x, _ in nodes]
    ys = [y for _, _, y in nodes]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)

    width  = max(x_max - x_min + 2, 4)
    height = max(y_max - y_min + 2, 3)

    fig, ax = plt.subplots(figsize=(max(width * 0.9, 6),
                                    max(height * 1.1, 4)))
    ax.set_xlim(x_min - 1, x_max + 1)
    ax.set_ylim(y_min - 1, y_max + 0.5)
    ax.axis('off')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=12)

    # Dibujar aristas
    def draw_edges(node: Node | None) -> None:
        if node is None:
            return
        x1, y1 = pos[id(node)]
        for child in (node.left, node.right):
            if child is not None:
                x2, y2 = pos[id(child)]
                ax.annotate('',
                            xy=(x2, y2 + NODE_RADIUS),
                            xytext=(x1, y1 - NODE_RADIUS),
                            arrowprops=dict(arrowstyle='-',
                                            color=EDGE_COLOR, lw=1.5))
                draw_edges(child)

    draw_edges(root)

    # Dibujar nodos
    for node, x, y in nodes:
        color = _node_color(node.value)
        circle = plt.Circle((x, y), NODE_RADIUS,
                             facecolor=color, edgecolor='white',
                             zorder=3, linewidth=1.5)
        ax.add_patch(circle)
        ax.text(x, y, _display_label(node.value),
                ha='center', va='center',
                fontsize=FONT_SIZE, fontweight='bold',
                color='white', zorder=4)

    # Leyenda
    legend_patches = [
        mpatches.Patch(color=OPERATOR_COLOR, label='Operador'),
        mpatches.Patch(color=OPERAND_COLOR,  label='Operando'),
        mpatches.Patch(color=EPSILON_COLOR,  label='ε (épsilon)'),
    ]
    ax.legend(handles=legend_patches, loc='lower right',
              fontsize=9, framealpha=0.8)

    plt.tight_layout()

    if filename is None:
        filename = title.replace(' ', '_') + '.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight',
                facecolor='white')
    plt.close()
    print(f'  → Árbol guardado: {filename}')


# ──────────────────────────────────────────────
# Utilidades de texto
# ──────────────────────────────────────────────

def tree_to_string(node: Node | None, indent: int = 0) -> str:
    """Representación textual indentada del árbol (para debug)."""
    if node is None:
        return ''
    label = _display_label(node.value)
    lines = [' ' * indent + label]
    if node.left  is not None:
        lines.append(tree_to_string(node.left,  indent + 4))
    if node.right is not None:
        lines.append(tree_to_string(node.right, indent + 4))
    return '\n'.join(lines)


if __name__ == '__main__':
    from shunting_yard import infix_to_postfix

    test = '(a*|b*)+'
    fmt, postfix = infix_to_postfix(test)
    print(f'Infix:   {test}')
    print(f'Postfix: {postfix}')
    root = build_tree(postfix)
    print(tree_to_string(root))
    draw_tree(root, title=f'Árbol: {test}', filename='test_tree.png')
