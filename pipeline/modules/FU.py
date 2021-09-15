function_unit_numbers = {
    "ALU": 4,
    "CSR": 1,
    "AGU": 3,
}


def new_function_units(with_data=False):
    function_units = {}
    for function_unit_type, function_unit_number in function_unit_numbers.items():
        function_units[function_unit_type] = (
            [{"latency": 0, "data": None} for i in range(function_unit_number)]
            if (with_data is True)
            else [{"latency": 0} for i in range(function_unit_number)]
        )

    return function_units
