"""
main.py — Laboratorio 3: Árbol Sintáctico de Expresiones Regulares
Teoría de la Computación

Uso:
    python main.py [archivo_input]

Si no se indica archivo, usa 'input.txt' por defecto.

Flujo completo por cada expresión:
    1. Leer la línea del archivo
    2. Convertir infix → postfix  (Shunting Yard, Lab 2)
    3. Construir el árbol sintáctico desde el postfix
    4. Mostrar el árbol en pantalla (texto) y guardar PNG
"""

import sys
import os
from shunting_yard import infix_to_postfix
from syntax_tree import build_tree, draw_tree, tree_to_string

SEPARATOR = '─' * 60


def process_regex(index: int, regex: str, output_dir: str) -> None:
    """Procesa una expresión regular: muestra la conversión y guarda el árbol."""
    regex = regex.strip()
    if not regex:
        return

    print(f'\n{SEPARATOR}')
    print(f'  Expresión {index}: {regex}')
    print(SEPARATOR)

    # 1. Infix → Postfix
    formatted, postfix = infix_to_postfix(regex)
    print(f'  Infix     : {regex}')
    print(f'  Formateado: {formatted}')
    print(f'  Postfix   : {postfix}')

    # 2. Árbol sintáctico
    root = build_tree(postfix)
    print('\n  Árbol (texto):')
    tree_str = tree_to_string(root, indent=4)
    print(tree_str)

    # 3. Guardar imagen PNG
    safe_name = regex.replace('(', '').replace(')', '').replace('*', 'star') \
                     .replace('|', 'or').replace('+', 'plus')  \
                     .replace('?', 'opt').replace(' ', '')      \
                     .replace('ε', 'eps')
    filename = os.path.join(output_dir, f'tree_{index}_{safe_name[:30]}.png')
    title = f'Expresión {index}: {regex}'
    draw_tree(root, title=title, filename=filename)


def main() -> None:
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'input.txt'

    if not os.path.isfile(input_file):
        print(f'[ERROR] No se encontró el archivo: {input_file}')
        sys.exit(1)

    # Carpeta de salida para las imágenes
    output_dir = os.path.join(os.path.dirname(input_file) or '.', 'trees')
    os.makedirs(output_dir, exist_ok=True)

    print('=' * 60)
    print('  LABORATORIO 3 — Árbol Sintáctico de Expresiones Regulares')
    print('=' * 60)
    print(f'\n  Leyendo: {input_file}')
    print(f'  Imágenes → {output_dir}/\n')

    with open(input_file, encoding='utf-8') as f:
        lines = [l for l in f if l.strip()]

    for i, line in enumerate(lines, start=1):
        process_regex(i, line.strip(), output_dir)

    print(f'\n{SEPARATOR}')
    print('  ¡Procesamiento completo!')
    print(f'  Se generaron {len(lines)} árbol(es) en: {output_dir}/')
    print(SEPARATOR)


if __name__ == '__main__':
    main()
