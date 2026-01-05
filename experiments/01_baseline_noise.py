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