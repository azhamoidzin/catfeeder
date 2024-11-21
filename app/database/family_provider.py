from database.db import Session, DFamily
from schemas.family import Family, FamilyInDB


def get_family_by_id(id_: int, db: Session) -> FamilyInDB | None:
    family = db.query(DFamily).where(DFamily.id == id_).first()
    if family:
        return FamilyInDB.model_validate(family)


def create_family(family: Family, db: Session) -> FamilyInDB | None:
    family_insert = DFamily(**family.dict())
    db.add(family_insert)
    db.commit()
    db.refresh(family_insert)
    return FamilyInDB.model_validate(family_insert)

