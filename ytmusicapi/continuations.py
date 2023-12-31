from ytmusicapi.navigation import nav


def get_continuations(
    results, continuation_type, limit, request_func, parse_func, ctoken_path="", reloadable=False
):
    items = []
    while "continuations" in results and (limit is None or len(items) < limit):
        additionalParams = (
            get_reloadable_continuation_params(results)
            if reloadable
            else get_continuation_params(results, ctoken_path)
        )
        response = request_func(additionalParams)
        if "continuationContents" in response:
            results = response["continuationContents"][continuation_type]
        else:
            break
        contents = get_continuation_contents(results, parse_func)
        if len(contents) == 0:
            break
        items.extend(contents)

    return items


def get_validated_continuations(
    results, continuation_type, limit, per_page, request_func, parse_func, ctoken_path=""
):
    items = []
    while "continuations" in results and len(items) < limit:
        additionalParams = get_continuation_params(results, ctoken_path)
        wrapped_parse_func = lambda raw_response: get_parsed_continuation_items(
            raw_response, parse_func, continuation_type
        )
        validate_func = lambda parsed: validate_response(parsed, per_page, limit, len(items))

        response = resend_request_until_parsed_response_is_valid(
            request_func, additionalParams, wrapped_parse_func, validate_func, 3
        )
        results = response["results"]
        items.extend(response["parsed"])

    return items


def get_parsed_continuation_items(response, parse_func, continuation_type):
    results = response["continuationContents"][continuation_type]
    return {"results": results, "parsed": get_continuation_contents(results, parse_func)}


def get_continuation_params(results, ctoken_path=""):
    ctoken = nav(results, ["continuations", 0, "next" + ctoken_path + "ContinuationData", "continuation"])
    return get_continuation_string(ctoken)


def get_reloadable_continuation_params(results):
    ctoken = nav(results, ["continuations", 0, "reloadContinuationData", "continuation"])
    return get_continuation_string(ctoken)


def get_continuation_string(ctoken):
    return "&ctoken=" + ctoken + "&continuation=" + ctoken


def get_continuation_contents(continuation, parse_func):
    for term in ["contents", "items"]:
        if term in continuation:
            return parse_func(continuation[term])

    return []


def resend_request_until_parsed_response_is_valid(
    request_func, request_additional_params, parse_func, validate_func, max_retries
):
    response = request_func(request_additional_params)
    parsed_object = parse_func(response)
    retry_counter = 0
    while not validate_func(parsed_object) and retry_counter < max_retries:
        response = request_func(request_additional_params)
        attempt = parse_func(response)
        if len(attempt["parsed"]) > len(parsed_object["parsed"]):
            parsed_object = attempt
        retry_counter += 1

    return parsed_object


def validate_response(response, per_page, limit, current_count):
    remaining_items_count = limit - current_count
    expected_items_count = min(per_page, remaining_items_count)

    # response is invalid, if it has less items then minimal expected count
    return len(response["parsed"]) >= expected_items_count
