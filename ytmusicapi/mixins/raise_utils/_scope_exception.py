scopes = ['library', 'uploads']

def scope_exception(scope):

    if scope and scope not in scopes:
        raise Exception(
            "Invalid scope provided. Please use one of the following scopes or leave out the parameter: "
            + ', '.join(scopes))    

def set_exception(scope, filter):

    if scope == scopes[1] and filter:
        raise Exception(
            "No filter can be set when searching uploads. Please unset the filter parameter when scope is set to "
            "uploads. "
        )