from fastapi import Query
from fastapi_pagination import Page, Params

from fastapi_pagination.utils import disable_installed_extensions_check
disable_installed_extensions_check()


class MyParams(Params):
    page: int = Query(1, ge=1, description="Номер страницы")
    size: int = Query(20, ge=1, le=50, description="Количество элементов на странице")


Page = Page.with_params(custom_params=MyParams)
