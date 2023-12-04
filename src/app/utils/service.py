from app.utils.dependencies import UOWDep


class BaseService:
    def __init__(self, uow: UOWDep):
        self.uow = uow
