from pydantic import BaseModel, conint, constr


class CreatingComment(BaseModel):
    stars: conint(ge=0, le=5)
    comment: constr(min_length=1)


class GettingCommentForUser(CreatingComment):
    id: int
    user_id: str
    date: str


class GettingCommentForItem(CreatingComment):
    id: int
    item_id: int
    date: str
