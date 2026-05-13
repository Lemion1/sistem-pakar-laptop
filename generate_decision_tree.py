"""
Generate decision tree diagram for the laptop expert system.
"""

from sistem_pakar import RULES

NODE_PREFIX = {
    'Pelajar / Mahasiswa Umum': 'P1',
    'Profesional / Bisnis': 'P2',
    'Gaming': 'P3',
    'Desain Grafis / Konten Kreator': 'P4',
    'Pengembang / Programmer': 'P5',
}

BUDGET_PREFIX = {
    'Ekonomis': 'E',
    'Menengah': 'M',
    'Tinggi': 'T',
    'Premium': 'P',
}


def format_node_id(kebutuhan, budget):
    return f"{NODE_PREFIX[kebutuhan]}_{BUDGET_PREFIX[budget]}"


def build_mermaid():
    lines = [
        'flowchart TB',
        '    A[Kebutuhan]'
    ]

    # Add kebutuhan nodes
    for kebutuhan, prefix in NODE_PREFIX.items():
        lines.append(f'    A --> {prefix}[{kebutuhan}]')

    # Add budget nodes and rule leaves
    for kebutuhan, budget_data in RULES.items():
        kb, budget = kebutuhan
        node_id = format_node_id(kb, budget)
        prefix = NODE_PREFIX[kb]
        lines.append(f'    {prefix} --> {node_id}[{budget}]')
        rule = budget_data
        gpu = rule['gpu']
        gpu_label = gpu if gpu != 'any' else 'any GPU'
        leaf_id = f"{node_id}_L"
        leaf_label = f"RAM ≥ {rule['ram_min']}GB\\nGPU: {gpu_label}\\nStorage ≥ {rule['storage_min']}GB"
        lines.append(f'    {node_id} --> {leaf_id}[{leaf_label}]')

    return "\n".join(lines)


if __name__ == '__main__':
    mermaid = build_mermaid()
    print('```mermaid')
    print(mermaid)
    print('```')
