import ast
import logging
from dataclasses import dataclass
from importlib import import_module
from inspect import getsource, isclass, isfunction, signature
from typing import Any, Callable, List, Type, Union

import libcst as cst
from fastapi import status
from fastapi.params import Depends
from fastapi.routing import APIRoute
from starlette.exceptions import HTTPException


logger = logging.getLogger("fastapi_responses")


@dataclass
class ExceptionArgs:
    status_code: int
    detail: Union[str, None]
    exception_class: Union[type[HTTPException], Any]


def get_string_from_cst_node(node):
    if isinstance(node, cst.FormattedStringText):
        return node.value
    elif isinstance(node, cst.Name):
        return node.value
    elif isinstance(node, cst.Dot):
        return "."
    elif isinstance(node, cst.FormattedStringExpression):
        parts_values = []
        for child in node.expression.children:
            parts_values.append(get_string_from_cst_node(child))
        return "{" + "".join(parts_values) + "}"
    elif isinstance(node, cst.FormattedString):
        parts_values = [get_string_from_cst_node(part) for part in node.parts]
        return "".join(parts_values)
    else:
        # Обработка других случаев, если необходимо
        return ""

def get_args_with_parentheses(
    node_exp: cst.BaseExpression, module: str, base_exception: HTTPException
) -> Union[ExceptionArgs, None]:
    call_name = None
    if isinstance(node_exp.func, cst.Attribute):
        call_name = node_exp.func.attr.value
    elif isinstance(node_exp.func, cst.Name):
        call_name = node_exp.func.value

    exception_class = getattr(module, call_name, None) if call_name else None
    is_exception = (
        exception_class
        and issubclass(exception_class, Exception)
        and issubclass(exception_class, base_exception)
    )
    status_code = None
    detail = None
    for arg in node_exp.args:
        if isinstance(arg.keyword, cst.Name) and arg.keyword.value == "status_code":
            if isinstance(arg.value, cst.Attribute):
                attr_value = getattr(status, arg.value.attr.value)
                status_code = attr_value
            else:
                status_code = arg.value.value

        elif isinstance(arg.keyword, cst.Name) and arg.keyword.value == "detail":
            if isinstance(arg.value, cst.FormattedString):
                # Использование функции для получения строки из узла
                detail = get_string_from_cst_node(arg.value)

                # parts_values = list()
                # for part in arg.value.parts:
                #     if isinstance(part, cst.FormattedStringText):
                #         parts_values.append(part.value)
                #     elif isinstance(part, cst.FormattedStringExpression):
                #         for children in part.expression.children:
                #             if isinstance(children, cst.Name):
                #                 parts_values.append(children.value)
                #             elif isinstance(children, cst.Dot):
                #                 parts_values.append(".")
                #     detail = "".join(parts_values)  # Используйте .raw для получения исходной строки
            else:
                detail = ast.literal_eval(arg.value.value)

        # elif isinstance(arg.keyword, cst.Name) and arg.keyword.value == "detail":
        #     if isinstance(arg.value, cst.FormattedString):
        #         detail = arg.value.raw  # Используйте .raw для получения исходной строки
        #     else:
        #         detail = ast.literal_eval(arg.value.value)

    if is_exception and not status_code:
        status_code = exception_class().status_code

    if is_exception and not detail:
        detail = exception_class().detail

    if isinstance(status_code, (str, int)):
        return ExceptionArgs(int(status_code), detail, exception_class)
    return None


def get_args_without_parentheses(
    node_exp: cst.BaseExpression, module: str, base_exception: HTTPException
) -> Union[ExceptionArgs, None]:
    exception_class = getattr(module, node_exp.value, None)
    is_exception = (
        exception_class
        and issubclass(exception_class, Exception)
        and issubclass(exception_class, base_exception)
    )
    status_code = None
    detail = None
    if is_exception:
        status_code = exception_class().status_code
        detail = exception_class().detail

    if isinstance(status_code, int):
        return ExceptionArgs(status_code, detail, exception_class)
    return None


NODE_TO_PARSE: dict[
    Type[cst.BaseExpression], Callable[..., Union[ExceptionArgs, None]]
] = {
    cst.Call: get_args_with_parentheses,
    cst.Name: get_args_without_parentheses,
}

FOUND_HTTP_EXCEPTIONS: List[HTTPException] = []
class RouterExceptionVisitor(cst.CSTVisitor):
    def __init__(self, endpoint, base_exception):
        self.http_exceptions: List[HTTPException] = []
        self.module = import_module(endpoint.__module__)
        self.base_exception = base_exception
        self.functions_to_visit = [endpoint]

    def visit_Call(self, node: cst.Call) -> None:
        func_name = None
        if isinstance(node.func, cst.Attribute):
            func_name = node.func.attr.value
        elif isinstance(node.func, cst.Name):
            func_name = node.func.value

        if func_name:
            module = import_module(self.module.__name__)
            func_or_class = getattr(module, func_name, None)
            if func_or_class:
                if isfunction(func_or_class):
                    self.functions_to_visit.append(func_or_class)
                elif isclass(func_or_class):
                    init_method = getattr(func_or_class, "__init__", None)
                    if init_method and isfunction(init_method):
                        self.functions_to_visit.append(init_method)
                    else:
                        self.functions_to_visit.append(func_or_class)

    def visit_Raise(self, node: cst.Raise):
        assert node.exc is not None
        strategy = NODE_TO_PARSE.get(type(node.exc), None)
        if strategy is not None:
            if isinstance(node.exc, cst.Call):
                result = strategy(node.exc, self.module, self.base_exception)
                if result:
                    temp_HTTPException: HTTPException = result.exception_class(
                        result.status_code, result.detail
                    )
                    self.http_exceptions.append(temp_HTTPException)
                    FOUND_HTTP_EXCEPTIONS.append(temp_HTTPException) # ААААААААААААААААААААААААААААААААААААААААААААААААААААААААААА

    def visit_Try(self, node: cst.Try):
        assert node.handlers is not None
        for handler in node.handlers:
            strategy = NODE_TO_PARSE.get(type(handler.type), None)
            if strategy is not None:
                for h_body_1 in handler.body.body:
                    for h_body_2 in h_body_1.body:
                        if isinstance(h_body_2.exc, cst.Call):
                            strategy = NODE_TO_PARSE.get(type(h_body_2.exc), None)
                            result = strategy(h_body_2.exc, self.module, self.base_exception)

                            if result:
                                temp_HTTPException: HTTPException = result.exception_class(
                                    result.status_code, result.detail
                                )
                                self.http_exceptions.append(temp_HTTPException)
                                FOUND_HTTP_EXCEPTIONS.append(
                                    temp_HTTPException)  # ААААААААААААААААААААААААААААААААААААААААААААААААААААААААААА

    # def visit_Await(self, node: cst.Await) -> None:
    #     if isinstance(node.value, cst.Call):
    #         self.visit_Call(node.value)
    #     else:
    #         print("JOPA")
    #         # Если это не cst.Call, возможно, нужно обработать другие случаи
    #         pass

    def visit_Assign(self, node: cst.Assign) -> None:
        ...
        module = import_module(self.module.__name__)
        status_code, detail = None, None
        node_value_args = list()
        if isinstance(node.value, cst.Await):
            node_value_args = node.value.expression.args

            if isinstance(node.value.expression.func.value, cst.Call):
                exception = getattr(module, node.value.expression.func.attr.value)
            elif isinstance(node.value.expression.func.value, cst.Call):
                exception = getattr(module, node.value.expression.func.value, None)

        else:
            node_value_args = node.value.args

        for arg in node_value_args:
            if type(arg.value) == cst.Integer:
                status_code = arg.value.value
            elif type(arg.value) == cst.SimpleString:
                detail = arg.value.value



        if exception and status_code:
            temp_HTTPException: HTTPException = exception(status_code, detail)
            self.http_exceptions.append(temp_HTTPException)

            FOUND_HTTP_EXCEPTIONS.append(temp_HTTPException)  # ААААААААААААААААААААААААААААААААААААААААААААААААААААААААААА


def extract_exceptions(
    route: APIRoute, base_exception=HTTPException
) -> List[HTTPException]:
    stack: list[Callable] = [route.endpoint]
    http_exceptions = []
    visited = set()

    while len(stack) > 0:
        func_or_class = stack.pop()
        try:
            sig = signature(func_or_class)
            for value in sig.parameters.values():
                if "Depends" in str(value) and hasattr(value.default, "dependency"):
                    dependency: Depends = value.default
                    stack.append(dependency.dependency)  # type: ignore
            source = getsource(func_or_class)
            abstract_syntax_tree = cst.parse_module(source)
            visitor = RouterExceptionVisitor(func_or_class, base_exception)
            abstract_syntax_tree.visit(visitor)

            # http_exceptions.extend(visitor.http_exceptions) #TODO: КОСТЫЛЬ В ВИДЕ FOUND_HTTP_EXCEPTIONS. в visitor'е очищается почему-то
            http_exceptions.extend(FOUND_HTTP_EXCEPTIONS)
            FOUND_HTTP_EXCEPTIONS.clear()
            stack.extend(
                f for f in visitor.functions_to_visit if f not in visited
            )  # Only add unvisited functions
        except Exception as error:
            logger.debug(f"Error processing function {func_or_class} -> {error}")
        finally:
            visited.add(func_or_class)
    return http_exceptions


def add_exception_to_openapi_schema(
    openapi_schema: dict, route: APIRoute, exc: HTTPException
) -> None:
    path = getattr(route, "path")
    methods = [method.lower() for method in getattr(route, "methods")]
    for method in methods:
        status_code = str(exc.status_code)
        if status_code not in openapi_schema["paths"][path][method]["responses"]:
            response_schema = {
                "description": exc.__class__.__name__,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "detail": {"type": "string", "example": exc.detail}
                            },
                        }
                    }
                },
            }
            openapi_schema["paths"][path][method]["responses"][
                status_code
            ] = response_schema

    return None
