from database.models import engine
from sqlalchemy.orm import sessionmaker
from database import models
import sqlalchemy as sa


class Mould:
    def __init__(self, mld_id: int, name: str, category: str, mld_type: str) -> None:
        self.mld_id = mld_id
        self.name = name
        self.category = category
        self.mld_type = mld_type
        """Mould type single/double"""
        self.count = None
        """Size wise count from 1-13"""
        self.running: list[int] = [0 for i in range(0, 13)]
        """Active mould counts size wise 1-13"""

    def add_mld_count(self, size: int, qty: int):
        """Sets mould count of given size"""
        if not self.count:
            mould_qty = [0 for i in range(0, 13)]
        else:
            mould_qty = list(self.count)

        mould_qty[size - 1] = qty
        self.count = tuple(mould_qty)


class Plan:

    # Include mould object in attrbs
    def __init__(self, mld_id: int, size: str, plan: int, pairs: int) -> None:
        self.mld_id = mld_id
        self.size = size
        """Size matrix of the plan"""
        self.plan = plan
        """Planned qty in case"""
        self.pairs = pairs
        """Total pairs in a case"""
        self.qty = None  # ToDo: Rather pass as tuple directly
        """Size wise plan qty 1-13"""
        self.mould: Mould = None  # ToDo: Assign the value through func matching mld id

    @property
    def mld_count(self):
        """Total moulds required for the plan"""
        return sum(1 for q in self.qty if q != 0)

    @property
    def mld_space(self):
        """Total mould space required for the plan"""
        max_qty = max(self.qty)
        return sum(q / max_qty for q in self.qty)

    @property
    def required_rot(self):
        """Maximum rotations required to complete the plan"""
        return max(self.qty)

    def add_size_qty(self, size, qty):
        """Add size wise plan qty"""
        if not self.qty:
            size_qty = [0 for i in range(0, 13)]
        else:
            size_qty = list(self.qty)
        size_qty[size - 1] = qty * self.plan
        self.qty = tuple(size_qty)


class Machine:
    def __init__(self, capacity: int, rotation_time: int) -> None:
        self.capacity = capacity
        """Total mould capacity in the machine in pairs"""
        self.rotation_time = rotation_time
        """Time required for 1 rotation"""
        self.used_space = 0
        """Used mould space in the machine"""
        self._rotations = 0
        """Total rotations"""
        self._change_count = 0
        """Plan change count"""

    @property
    def add_rotations(self, rot: int):
        self._rotations += rot

    @property
    def add_change_count(self):
        self._change_count += 1


if __name__ == "__main__":
    Session = sessionmaker(bind=engine)
    qm_results = None
    moulds: dict[int, Mould] = {}

    # Mould list modeling
    with Session() as s:
        qm_results = (
            s.query(
                models.MouldSet.id,
                models.MouldModel.mould_no,
                models.MouldSet.category,
                models.MouldSet.mould_type,
                models.Mould.size,
                models.Mould.quantity,
            )
            .select_from(models.MouldSet)
            .join(models.MouldModel)
            .join(models.Mould)
            .order_by(models.MouldSet.id)
            .all()
        )

    for mld in qm_results:
        size, qty = mld[-2:]
        if mld[0] not in moulds.keys():
            moulds[mld[0]] = Mould(
                mld_id=mld[0], name=mld[1], category=mld[2], mld_type=mld[3]
            )
        moulds[mld[0]].add_mld_count(size, qty)

    # Plan list modeling
    results = None
    with Session() as s:
        results = (
            s.query(
                models.MouldSet.id,
                models.PlanCurrent.size,
                models.PlanCurrent.plan,
                models.PlanCurrent.pairs,
                models.PackingOrder.size,
                sa.func.sum(models.PackingOrder.quantity),
            )
            .select_from(models.Article)
            .join(models.ArticleModel, models.ArticleModel.id == models.Article.article)
            .join(models.Category, models.Category.id == models.Article.category)
            .join(models.Color, models.Color.id == models.Article.color)
            .join(models.MouldSet, models.MouldSet.id == models.Article.mould)
            .join(
                models.PlanCurrent,
                (
                    (models.PlanCurrent.art_no == models.ArticleModel.art_no)
                    & (models.PlanCurrent.color == models.Color.name)
                    & (models.PlanCurrent.category == models.Category.name)
                ),
            )
            .join(
                models.PackingStyle,
                (
                    (models.PackingStyle.category == models.Category.id)
                    & (models.PackingStyle.size_matrix == models.PlanCurrent.size)
                    & (models.PackingStyle.pairs == models.PlanCurrent.pairs)
                ),
            )
            .join(
                models.PackingOrder,
                models.PackingOrder.packing == models.PackingStyle.id,
            )
            .group_by(
                models.MouldSet.id,
                models.PlanCurrent.size,
                models.PlanCurrent.plan,
                models.PlanCurrent.pairs,
                models.PackingOrder.size,
            )
            .where(models.PackingOrder.quantity != 0)
            .all()
        )
