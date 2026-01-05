#01_baseline_noise is a control circuit to measure noise in an average circuit
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeKyoto

circuit = QuantumCircuit(2)

#Running Bell State to ensure accuracy in the results and detect errors.
circuit.h(0)
circuit.cx(0,1)
#Measuring results for data analysis
circuit.measure_all()

#building the variables to compare both backends
ideal_backend = AerSimulator()
noisy_backend = AerSimulator.from_backend(FakeKyoto())

#Transpiling the circuit with the kyoto backend for comparison
qc_transpiled = transpile(circuit, noisy_backend)

#Iniciating both ideal jand noisy jobs
ideal_job = ideal_backend.run(circuit, shots=4000)
ideal_counts = ideal_job.result().get_counts()

noisy_job = noisy_backend.run(qc_transpiled, shots=4000)
noisy_counts = noisy_job.result().get_counts()

print(ideal_counts)
print(noisy_counts)
