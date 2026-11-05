"""Educational QAOA helpers for the QSIP hackathon.

All functions are deterministic except quantum sampling. Uses only public,
synthetic graphs. Bit conventions: bits[i] corresponds to graph node i.
"""
from itertools import product
import numpy as np
import networkx as nx

BEGINNER_EDGES = [
    (0, 1), (0, 3), (0, 4), (1, 2), (1, 3), (1, 5),
    (2, 5), (2, 4), (3, 5), (3, 4), (4, 5)
]


def starter_graph():
    graph = nx.Graph()
    graph.add_nodes_from(range(6))
    graph.add_weighted_edges_from((i, j, 1.0) for i, j in BEGINNER_EDGES)
    return graph


def weighted_edges(graph):
    return [(int(u), int(v), float(data.get('weight', 1.0)))
            for u, v, data in graph.edges(data=True)]


def bits_from_qiskit(label):
    """Qiskit displays c[n-1]...c[0]; return bits in node index order."""
    return tuple(int(char) for char in label.replace(' ', '')[::-1])


def cut_score(bits, edges):
    return float(sum(w for i, j, w in edges if bits[i] != bits[j]))


def brute_force(n, score_fn):
    scores = [(float(score_fn(bits)), bits) for bits in product((0, 1), repeat=n)]
    return max(scores, key=lambda pair: pair[0]), scores


def qaoa_circuit(n, edges, gammas=(0.5,), betas=(0.4,), measure=True):
    """QAOA for maximizing sum_ij w_ij * (x_i xor x_j).

    Negative edge weights are allowed; this supports modularity via a signed
    complete graph. The cost unitary is exp(-i * gamma * C).
    """
    from qiskit import QuantumCircuit
    if len(gammas) != len(betas) or not gammas:
        raise ValueError('gammas and betas must be equally sized nonempty arrays')
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for gamma, beta in zip(gammas, betas):
        for i, j, w in edges:
            # RZZ(theta)=exp(-i theta/2 Z_i Z_j).
            # C_ij=w(1-Z_iZ_j)/2, hence theta=-gamma*w.
            qc.rzz(-float(gamma) * w, i, j)
        for i in range(n):
            qc.rx(2.0 * float(beta), i)
    if measure:
        qc.measure_all()
    return qc


def qaoa_probabilities(n, edges, gammas=(0.5,), betas=(0.4,)):
    from qiskit.quantum_info import Statevector
    state = Statevector.from_instruction(qaoa_circuit(n, edges, gammas, betas, measure=False))
    return np.abs(state.data) ** 2


def qaoa_expected_score(n, edges, gamma, beta, score_fn=None):
    if score_fn is None:
        score_fn = lambda bits: cut_score(bits, edges)
    probabilities = qaoa_probabilities(n, edges, (gamma,), (beta,))
    values = np.array([score_fn(tuple((i >> j) & 1 for j in range(n)))
                       for i in range(2**n)], dtype=float)
    return float(probabilities @ values)


def optimize_p1(n, edges, score_fn=None, maxiter=80):
    from scipy.optimize import minimize
    if score_fn is None:
        score_fn = lambda bits: cut_score(bits, edges)
    result = minimize(lambda parameters: -qaoa_expected_score(
        n, edges, parameters[0], parameters[1], score_fn),
        x0=np.array([0.7, 0.4]), method='Nelder-Mead',
        options={'maxiter': maxiter, 'xatol': 2e-3, 'fatol': 1e-3})
    return result


def simulate_counts(circuit, shots=1024, seed=42):
    """Local quantum-circuit sampling, no credentials required."""
    from qiskit import transpile
    from qiskit_aer import AerSimulator
    backend = AerSimulator()
    compiled = transpile(circuit, backend)
    return backend.run(compiled, shots=shots, seed_simulator=seed).result().get_counts()


def best_from_counts(counts, score_fn):
    """Find highest scoring observed output, not merely most frequent bitstring."""
    candidate_list = [(float(score_fn(bits_from_qiskit(label))), label, int(count))
                      for label, count in counts.items()]
    return max(candidate_list, key=lambda item: item[0])


def brain_graph(n=6, seed=4):
    """Synthetic, positive weighted, two-block functional-connectivity toy example."""
    if n < 4 or n % 2 != 0:
        raise ValueError('use even n >= 4')
    rng = np.random.default_rng(seed)
    graph = nx.Graph()
    graph.add_nodes_from(range(n))
    half = n // 2
    for i in range(n):
        for j in range(i + 1, n):
            within = (i < half) == (j < half)
            weight = float(rng.uniform(.75, 1.0) if within else rng.uniform(.03, .20))
            graph.add_edge(i, j, weight=weight)
    return graph


def modularity_matrix(graph):
    nodes = list(range(graph.number_of_nodes()))
    A = nx.to_numpy_array(graph, nodelist=nodes, weight='weight')
    strengths = A.sum(axis=1)
    two_m = float(A.sum())
    if two_m <= 0:
        raise ValueError('Graph must have positive total weight')
    B = A - np.outer(strengths, strengths) / two_m
    return A, B, two_m


def binary_modularity(bits, B, two_m):
    labels = np.asarray(bits)
    same = (labels[:, None] == labels[None, :]).astype(float)
    return float(np.sum(B * same) / two_m)


def modularity_to_signed_cut(B, two_m):
    """For two groups: maximize modularity iff maximize this signed cut.

    Q = constant + sum_{i<j} (-2 B_ij / two_m) [x_i != x_j].
    Thus the weighted Max-Cut form can be used without constraining group sizes.
    """
    n = B.shape[0]
    return [(i, j, float(-2.0 * B[i, j] / two_m))
            for i in range(n) for j in range(i + 1, n)]


def draw_graph(graph, bits=None, title=None, positions=None):
    import matplotlib.pyplot as plt
    if positions is None:
        positions = nx.spring_layout(graph, seed=12)
    plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Helvetica Neue', 'Helvetica', 'Nimbus Sans', 'Arial', 'DejaVu Sans'], 'axes.edgecolor': '#151515', 'text.color': '#151515', 'axes.labelcolor': '#151515', 'figure.facecolor': 'white', 'axes.facecolor': 'white'})
    fig, ax = plt.subplots(figsize=(7, 4.5))
    colors = ['#dc202b' if bits is None or bits[i] == 0 else '#151515'
              for i in graph.nodes()]
    weights = [graph[u][v].get('weight', 1) for u, v in graph.edges()]
    nx.draw_networkx(graph, pos=positions, node_color=colors, edge_color='#a0a09c',
                     node_size=650, width=[1.0 + 2*w for w in weights],
                     font_weight='bold', font_color='white', ax=ax)
    ax.axis('off')
    if title:
        ax.set_title(title, loc='left', pad=14)
    fig.tight_layout()
    return fig, ax
