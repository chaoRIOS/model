function_unit_numbers = [
    {
        # Pipelined ALU
        # Use multiple multi-cycle MUL/DIV to simulate 1 pipelined ALU
        "ALU": 1,
        "MUL": 4,
        "DIV": 4,
        # Other function units in cluster
        "CSR": 1,
        "AGU": 1,
        "BR": 1,
    },
    {
        "ALU": 1,
        "MUL": 4,
        "DIV": 4,
        
        "AGU": 1,
    },
    {
        "ALU": 1,
        "MUL": 4,
        "DIV": 4,

        "AGU": 1,
    },
    {
        "ALU": 1,
        "MUL": 4,
        "DIV": 4,

        "BR": 1,
    },
]


def new_function_units(with_data=False):
    total_function_units = []
    for i in range(len(function_unit_numbers)):
        function_units = {}
        for function_unit_type, function_unit_number in function_unit_numbers[i].items():
            function_units[function_unit_type] = (
                [{"latency": 0, "data": None} for i in range(function_unit_number)]
                if (with_data is True)
                else [{"latency": 0} for i in range(function_unit_number)]
            )
        total_function_units.append(function_units)
    return total_function_units
