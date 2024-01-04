from app.modules.users.utils.reactions import Reaction
from app.utils.unit_of_work import UnitOfWork


class UserService:
    async def get_user_reactions(self, uow: UnitOfWork, user_id: int):
        async with uow:
            reactions = await uow.reaction.filter(user_id=user_id)
            return reactions

    async def make_reaction(self, uow: UnitOfWork, user_id: int, artwork_id: int):
        async with uow:
            reactions = await uow.reaction.filter(user_id=user_id, artworks_id=artwork_id)
            if reactions:
                reaction = reactions[0]
                await uow.reaction.delete(reaction.id)
            else:
                reaction = {"user_id": user_id, "artworks_id": artwork_id}
                reaction = await uow.reaction.create(reaction)
            await uow.commit()
            return reaction
