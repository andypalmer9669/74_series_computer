import pytest

from eight_bit_computer.language.operations import set_op
from eight_bit_computer.language.utils import get_machine_code_byte_template
from eight_bit_computer.exceptions import InstructionParsingError

@pytest.mark.parametrize("test_input,expected", [
    (
        "A",
        "00111001",
    ),
    (
        "B",
        "00111010",
    ),
])
def test_get_instruction_byte(test_input, expected):
    assert set_op.get_instruction_byte(test_input) == expected


def generate_parse_line_test_data():
    ret = []

    test_input = ""
    expected = []
    ret.append((test_input, expected))

    test_input = "   \t"
    expected = []
    ret.append((test_input, expected))

    test_input = "LOAD [#123] A"
    expected = []
    ret.append((test_input, expected))

    test_input = "SET A #123"
    mc_0 = get_machine_code_byte_template()
    mc_0["machine_code"] = "00111001"
    mc_1 = get_machine_code_byte_template()
    mc_1["constant"] = "#123"
    ret.append((test_input, [mc_0, mc_1]))

    test_input = "   SET  B   monkey   "
    mc_0 = get_machine_code_byte_template()
    mc_0["machine_code"] = "00111010"
    mc_1 = get_machine_code_byte_template()
    mc_1["constant"] = "monkey"
    ret.append((test_input, [mc_0, mc_1]))

    return ret


@pytest.mark.parametrize(
    "test_input,expected", generate_parse_line_test_data()
)
def test_parse_line(test_input, expected):
    assert set_op.parse_line(test_input) == expected


@pytest.mark.parametrize("test_input", [
    "SET",
    "SET A",
    "SET #123",
    "SET BLAH #123",
    "SET A #123 FOO"
])
def test_parse_line_raises(test_input):
    with pytest.raises(InstructionParsingError):
        set_op.parse_line(test_input)
