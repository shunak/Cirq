# Copyright 2018 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

import cirq
from cirq.contrib.paulistring import (
    ConvertToPauliStringPhasors, PauliStringPhasor
)


def test_convert():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit.from_ops(
        cirq.X(q0),
        cirq.Y(q1) ** 0.25,
        cirq.Z(q0) ** 0.125,
        cirq.H(q1),
    )
    c_orig = cirq.Circuit(circuit)
    ConvertToPauliStringPhasors().optimize_circuit(circuit)

    cirq.testing.assert_allclose_up_to_global_phase(
        circuit.to_unitary_matrix(),
        c_orig.to_unitary_matrix(),
        atol=1e-7)
    assert circuit.to_text_diagram() == """
0: ───[X]────────[Z]^0.125─────────

1: ───[Y]^0.25───[Y]^-0.5────[Z]───
""".strip()


def test_convert_keep_clifford():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit.from_ops(
        cirq.X(q0),
        cirq.Y(q1) ** 0.25,
        cirq.Z(q0) ** 0.125,
        cirq.CliffordGate.H(q1),
    )
    c_orig = cirq.Circuit(circuit)
    ConvertToPauliStringPhasors(keep_clifford=True).optimize_circuit(circuit)

    cirq.testing.assert_allclose_up_to_global_phase(
        circuit.to_unitary_matrix(),
        c_orig.to_unitary_matrix(),
        atol=1e-7)
    assert circuit.to_text_diagram() == """
0: ───X──────────[Z]^0.125───

1: ───[Y]^0.25───H───────────
""".strip()


def test_already_converted():
    q0 = cirq.LineQubit(0)
    circuit = cirq.Circuit.from_ops(
        PauliStringPhasor(cirq.PauliString.from_single(q0, cirq.Pauli.X)),
    )
    c_orig = cirq.Circuit(circuit)
    ConvertToPauliStringPhasors().optimize_circuit(circuit)

    assert circuit == c_orig


def test_ignore_unsupported_gate():
    class UnsupportedDummy(cirq.Gate):
        pass

    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit.from_ops(
        UnsupportedDummy()(q0, q1),
    )
    c_orig = cirq.Circuit(circuit)
    ConvertToPauliStringPhasors(ignore_failures=True
                                     ).optimize_circuit(circuit)

    assert circuit == c_orig


def test_fail_unsupported_gate():
    class UnsupportedDummy(cirq.Gate):
        pass

    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit.from_ops(
        UnsupportedDummy()(q0, q1),
    )
    with pytest.raises(TypeError):
        ConvertToPauliStringPhasors().optimize_circuit(circuit)
