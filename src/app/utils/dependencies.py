from typing import Annotated

from fastapi import Depends

from app.utils.unit_of_work import UnitOfWork

UOWDep = Annotated[UnitOfWork, Depends(UnitOfWork)]
