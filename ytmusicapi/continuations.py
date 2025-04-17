from collections.abc import Callable
from typing import Any

from ytmusicapi.navigation import nav
from ytmusicapi.type_alias import (
    JsonDict,
    JsonList,
    ParseFuncDictType,
    ParseFuncType,
    RequestFuncBodyType,
    RequestFuncType,
)

CONTINUATION_TOKEN = ["continuationItemRenderer", "continuationEndpoint", "continuationCommand", "token"]
CONTINUATION_ITEMS = ["onResponseReceivedActions", 0, "appendContinuationItemsAction", "continuationItems"]


def get_continuation_token(results: JsonList) -> str | None:
    return nav(results[-1], CONTINUATION_TOKEN, True)


def get_continuations_2025(
    results: JsonDict,
    limit: int | None,
    request_func: RequestFuncBodyType,
    parse_func: ParseFuncType,
) -> JsonList:
    items: JsonList = []
    continuation_token = get_continuation_token(results["contents"])
    while continuation_token and (limit is None or len(items) < limit):
        response = request_func({"continuation": continuation_token})
        continuation_items = nav(response, CONTINUATION_ITEMS, True)
        if not continuation_items:
            break

        contents = parse_func(continuation_items)
        if len(contents) == 0:
            break
        items.extend(contents)
        continuation_token = get_continuation_token(continuation_items)

    return items


def get_reloadable_continuations(
    results: JsonDict,
    continuation_type: str,
    limit: int | None,
    request_func: RequestFuncType,
    parse_func: ParseFuncType,
) -> JsonList:
    """Reloadable continuations are a special case that only exists on the playlists page (suggestions)."""
    additionalParams = get_reloadable_continuation_params(results)
    return get_continuations(
        results, continuation_type, limit, request_func, parse_func, additionalParams=additionalParams
    )


def get_continuations(
    results: JsonDict,
    continuation_type: str,
    limit: int | None,
    request_func: RequestFuncType,
    parse_func: ParseFuncType,
    ctoken_path: str = "",
    additionalParams: str | None = None,
) -> JsonList:
    """

    :param results: result list from request data
    :param continuation_type: type of continuation,
            determines which subkey will be used to navigate the continuation return data
    :param limit: determines minimum of how many items to retrieve in total.
            None to retrieve all items until no more continuations are returned
    :param request_func: the request func to use to get the continuations
    :param parse_func: the parse func to apply on the returned continuations
    :param ctoken_path: rarely used specifier applied to retrieve the ctoken ("next<ctoken_path>ContinuationData").
            Default empty string
    :param additionalParams: Optional additional params to pass to the request func. Default: use get_continuation_params
    :return: list of parsed continuation results
    """
    items: JsonList = []
    while "continuations" in results and (limit is None or len(items) < limit):
        additional_params = additionalParams or get_continuation_params(results, ctoken_path)
        response = request_func(additional_params)
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
    results: JsonDict,
    continuation_type: str,
    limit: int,
    per_page: int,
    request_func: RequestFuncType,
    parse_func: ParseFuncType,
    ctoken_path: str = "",
) -> JsonList:
    items: JsonList = []
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


def get_parsed_continuation_items(
    response: JsonDict, parse_func: ParseFuncType, continuation_type: str
) -> JsonDict:
    results = response["continuationContents"][continuation_type]
    return {"results": results, "parsed": get_continuation_contents(results, parse_func)}


def get_continuation_params(results: JsonDict, ctoken_path: str = "") -> str:
    ctoken = nav(results, ["continuations", 0, "next" + ctoken_path + "ContinuationData", "continuation"])
    return get_continuation_string(ctoken)


def get_reloadable_continuation_params(results: JsonDict) -> str:
    ctoken = nav(results, ["continuations", 0, "reloadContinuationData", "continuation"])
    return get_continuation_string(ctoken)


def get_continuation_string(ctoken: str) -> str:
    """
    Returns the continuation string used in the continuation request

    :param ctoken: the unique continuation token
    """
    return "&ctoken=" + ctoken + "&continuation=" + ctoken


def get_continuation_contents(continuation: JsonDict, parse_func: ParseFuncType) -> JsonList:
    for term in ["contents", "items"]:
        if term in continuation:
            return parse_func(continuation[term])

    return []


def resend_request_until_parsed_response_is_valid(
    request_func: RequestFuncType,
    request_additional_params: str,
    parse_func: ParseFuncDictType,
    validate_func: Callable[[dict[str, Any]], bool],
    max_retries: int,
) -> JsonDict:
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


def validate_response(response: JsonDict, per_page: int, limit: int, current_count: int) -> bool:
    remaining_items_count = limit - current_count
    expected_items_count = min(per_page, remaining_items_count)

    # response is invalid, if it has less items then minimal expected count
    return len(response["parsed"]) >= expected_items_count
