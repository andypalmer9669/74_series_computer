import pytest
from copy import deepcopy

from eight_bit_computer import assembler
from eight_bit_computer.data_structures import (
    get_assembly_line_template, get_machine_code_byte_template
)
from eight_bit_computer.exceptions import LineProcessingError, AssemblyError


@pytest.mark.parametrize("test_input,variable_start_offset", [
    (
        [
            "fegwkefjghwfjkhgwekjfgh",
        ],
        0,
    )
])
def test_process_assembly_lines_raises(test_input, variable_start_offset):
    with pytest.raises(AssemblyError):
        assembler.process_assembly_lines(
            test_input, variable_start_offset=variable_start_offset
        )


def get_test_process_line_data():
    """
    Test data for the process line test
    """
    tests = []
    test_input = ""
    test_output = get_assembly_line_template()
    tests.append((test_input, test_output))

    test_input = "// comment"
    test_output = get_assembly_line_template()
    test_output["raw"] = "// comment"
    tests.append((test_input, test_output))

    test_input = "@label"
    test_output = get_assembly_line_template()
    test_output["raw"] = "@label"
    test_output["clean"] = "@label"
    test_output["defined_label"] = "@label"
    test_output["defines_label"] = True
    tests.append((test_input, test_output))

    test_input = "$variable"
    test_output = get_assembly_line_template()
    test_output["raw"] = "$variable"
    test_output["clean"] = "$variable"
    test_output["defined_variable"] = "$variable"
    test_output["defines_variable"] = True
    tests.append((test_input, test_output))

    test_input = "    @label // comment"
    test_output = get_assembly_line_template()
    test_output["raw"] = "    @label // comment"
    test_output["clean"] = "@label"
    test_output["defined_label"] = "@label"
    test_output["defines_label"] = True
    tests.append((test_input, test_output))

    test_input = "    $variable // comment"
    test_output = get_assembly_line_template()
    test_output["raw"] = "    $variable // comment"
    test_output["clean"] = "$variable"
    test_output["defined_variable"] = "$variable"
    test_output["defines_variable"] = True
    tests.append((test_input, test_output))

    return tests


@pytest.mark.parametrize("test_input,expected", get_test_process_line_data())
def test_process_line(test_input, expected):
    assert assembler.process_line(test_input) == expected


@pytest.mark.parametrize("test_input", [
    "fwgfkwghfkjhwgekjhgwkejg",
])
def test_process_line_raises(test_input):
    with pytest.raises(LineProcessingError):
        assembler.process_line(test_input)


@pytest.mark.parametrize("test_input,expected", [
    (
        "",
        "",
    ),
    (
        "//",
        "",
    ),
    (
        "/hello /world!",
        "/hello /world!",
    ),
    (
        "blah blah//",
        "blah blah",
    ),
    (
        "before//after",
        "before",
    ),
    (
        "   before   //after   ",
        "   before   ",
    ),
    (
        "LOAD [A] B",
        "LOAD [A] B",
    ),
])
def test_remove_comments(test_input, expected):
    assert assembler.remove_comments(test_input) == expected


@pytest.mark.parametrize("test_input,expected", [
    (
        "",
        "",
    ),
    (
        "      ",
        "",
    ),
    (
        "LOAD [$foo] A",
        "LOAD [$foo] A",
    ),
    (
        "     LOAD     [$foo]     A    ",
        "LOAD [$foo] A",
    ),
    (
        "\tLOAD\t\t[$foo]     A  \t  ",
        "LOAD [$foo] A",
    ),
    (
        "LOAD [  $foo  ] A",
        "LOAD [ $foo ] A",
    ),
    (
        "   LOAD [$foo] A",
        "LOAD [$foo] A",
    ),
    (
        "LOAD [$foo] A   ",
        "LOAD [$foo] A",
    ),
    (
        "SET A  #14  ",
        "SET A #14",
    ),
])
def test_remove_excess_whitespace(test_input, expected):
    assert assembler.remove_excess_whitespace(test_input) == expected


@pytest.mark.parametrize("test_input", [
    "fwgfkwghfkjhwgekjhgwkejg",
])
def test_machine_code_templates_from_line_raises(test_input):
    with pytest.raises(LineProcessingError):
        assembler.machine_code_bytes_from_line(test_input)


def gen_test_validate_and_identify_constants_data():
    ret = []

    test_input = get_machine_code_byte_template()
    test_input["bitstring"] = "01101100"
    test_input["byte_type"] = "instruction"
    expected_output = deepcopy(test_input)
    ret.append(([test_input], [expected_output]))

    test_input = get_machine_code_byte_template()
    test_input["byte_type"] = "constant"
    test_input["constant"] = "@label"
    expected_output = deepcopy(test_input)
    expected_output["constant_type"] = "label"
    ret.append(([test_input], [expected_output]))

    test_input = get_machine_code_byte_template()
    test_input["byte_type"] = "constant"
    test_input["constant"] = "$variable"
    expected_output = deepcopy(test_input)
    expected_output["constant_type"] = "variable"
    ret.append(([test_input], [expected_output]))

    test_input = get_machine_code_byte_template()
    test_input["byte_type"] = "constant"
    test_input["constant"] = "#123"
    expected_output = deepcopy(test_input)
    expected_output["constant_type"] = "number"
    expected_output["number_value"] = 123
    ret.append(([test_input], [expected_output]))

    test_input_0 = get_machine_code_byte_template()
    test_input_0["bitstring"] = "01101100"
    test_input_0["byte_type"] = "instruction"
    expected_output_0 = deepcopy(test_input_0)
    test_input_1 = get_machine_code_byte_template()
    test_input_1["byte_type"] = "constant"
    test_input_1["constant"] = "@label"
    expected_output_1 = deepcopy(test_input_1)
    expected_output_1["constant_type"] = "label"
    ret.append(
        (
            [test_input_0, test_input_1],
            [expected_output_0, expected_output_1]
        )
    )

    return ret


@pytest.mark.parametrize(
    "test_input,expected", gen_test_validate_and_identify_constants_data()
)
def test_validate_and_identify_constants(test_input, expected):
    assembler.validate_and_identify_constants(test_input)
    assert test_input == expected


def gen_validate_and_identify_constants_raises_data():
    ret = []

    test_input = get_machine_code_byte_template()
    test_input["byte_type"] = "constant"
    test_input["constant"] = "fwgjfgwjfgkjh"
    ret.append([test_input])

    test_input = get_machine_code_byte_template()
    test_input["byte_type"] = "constant"
    test_input["constant"] = "@number$variable#123"
    ret.append([test_input])

    test_input = get_machine_code_byte_template()
    test_input["byte_type"] = "constant"
    test_input["constant"] = "#9999"
    ret.append([test_input])

    return ret


@pytest.mark.parametrize(
    "test_input", gen_validate_and_identify_constants_raises_data()
)
def test_validate_and_identify_constants_raises(test_input):
    with pytest.raises(LineProcessingError):
        assembler.validate_and_identify_constants(test_input)


def test_assign_labels(processed_assembly_lines):
    expected_lines = deepcopy(processed_assembly_lines)
    expected_lines[2]["assigned_label"] = "@label1"
    expected_lines[2]["has_label_assigned"] = True
    expected_lines[5]["assigned_label"] = "@label2"
    expected_lines[5]["has_label_assigned"] = True
    expected_lines[10]["assigned_label"] = "@label3"
    expected_lines[10]["has_label_assigned"] = True
    assembler.assign_labels(processed_assembly_lines)
    assert processed_assembly_lines == expected_lines


def test_resolve_labels(processed_assembly_lines):
    processed_assembly_lines[2]["assigned_label"] = "@label1"
    processed_assembly_lines[2]["has_label_assigned"] = True
    processed_assembly_lines[5]["assigned_label"] = "@label2"
    processed_assembly_lines[5]["has_label_assigned"] = True
    processed_assembly_lines[10]["assigned_label"] = "@label3"
    processed_assembly_lines[10]["has_label_assigned"] = True
    expected_lines = deepcopy(processed_assembly_lines)
    expected_lines[6]["mc_bytes"][1]["bitstring"] = "00000000"
    assembler.resolve_labels(processed_assembly_lines)
    assert processed_assembly_lines == expected_lines


def test_label_map(processed_assembly_lines):
    processed_assembly_lines[2]["assigned_label"] = "@label1"
    processed_assembly_lines[2]["has_label_assigned"] = True
    processed_assembly_lines[5]["assigned_label"] = "@label2"
    processed_assembly_lines[5]["has_label_assigned"] = True
    processed_assembly_lines[10]["assigned_label"] = "@label3"
    processed_assembly_lines[10]["has_label_assigned"] = True
    expected_label_map = {
        "@label1": "00000000",
        "@label2": "00000010",
        "@label3": "00001000",
    }
    label_map = assembler.create_label_map(processed_assembly_lines)
    assert label_map == expected_label_map


def test_resolve_numbers(processed_assembly_lines):
    expected_lines = deepcopy(processed_assembly_lines)
    expected_lines[8]["mc_bytes"][1]["bitstring"] = "01111011"
    assembler.resolve_numbers(processed_assembly_lines)
    assert processed_assembly_lines == expected_lines


def test_resolve_variables_no_offset(processed_assembly_lines):
    expected_lines = deepcopy(processed_assembly_lines)
    expected_lines[2]["mc_bytes"][1]["bitstring"] = "00000001"
    expected_lines[5]["mc_bytes"][1]["bitstring"] = "00000010"
    expected_lines[10]["mc_bytes"][1]["bitstring"] = "00000011"
    expected_lines[11]["mc_bytes"][1]["bitstring"] = "00000000"
    assembler.resolve_variables(processed_assembly_lines, 0)
    assert processed_assembly_lines == expected_lines


def test_resolve_variables_with_offset(processed_assembly_lines):
    expected_lines = deepcopy(processed_assembly_lines)
    expected_lines[2]["mc_bytes"][1]["bitstring"] = "00001001"
    expected_lines[5]["mc_bytes"][1]["bitstring"] = "00001010"
    expected_lines[10]["mc_bytes"][1]["bitstring"] = "00001011"
    expected_lines[11]["mc_bytes"][1]["bitstring"] = "00001000"
    assembler.resolve_variables(processed_assembly_lines, 8)
    assert processed_assembly_lines == expected_lines


def test_create_variable_map_no_offset(processed_assembly_lines):
    exected_variable_map = {
        "$variable0": "00000000",
        "$variable1": "00000001",
        "$variable2": "00000010",
        "$variable3": "00000011",
        "$variable4": "00000100",
    }
    variable_map = assembler.create_variable_map(processed_assembly_lines, 0)
    assert variable_map == exected_variable_map


def test_create_variable_map_with_offset(processed_assembly_lines):
    exected_variable_map = {
        "$variable0": "00001000",
        "$variable1": "00001001",
        "$variable2": "00001010",
        "$variable3": "00001011",
        "$variable4": "00001100",
    }
    variable_map = assembler.create_variable_map(processed_assembly_lines, 8)
    assert variable_map == exected_variable_map
