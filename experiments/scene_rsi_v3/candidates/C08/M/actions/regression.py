"""M-selected structural/edit regression; edit tests require an explicit real target."""
def run(context):
    from regression import execute_test
    parameters=context['parameters']
    test=parameters['test']
    target=parameters['object_id'] if test in ['material_preservation','composite_move'] else None
    return execute_test(test,target)
