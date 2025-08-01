from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy import update as sa_update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.db import DBBaseModel


DBModel = TypeVar("DBModel", bound=DBBaseModel)
DTO = TypeVar("DTO")
IDType = TypeVar("IDType")


class BaseRepository(Generic[DBModel, DTO, IDType], ABC):
    """
    Repository mixin with common methods for all repositories:
    - get_by_id(id: IDType) -> DTO | None
    - get_all() -> list[DTO]
    - create(dto: DTO) -> DTO
    - update(dto: DTO) -> DTO
    - delete(id: IDType) -> None

    To use this mixin, inherit from it and implement the methods
    - map_model_to_dto() method to map DBModel fields to DTO fields
    - map_dto_to_model() method to map DTO fields to DBModel fields
    """

    def __init__(
        self,
        session: AsyncSession,
        model_class: type[DBModel],
        id_field: str = "id",
        already_exists_exception_class: type[Exception] = IntegrityError,
        not_found_exception_class: type[Exception] = NoResultFound,
    ):
        """
        Initialize the repository with a session and model class.
        :param session: SQLAlchemy async session
        :param model_class: SQLAlchemy model class
        :param id_field: Name of the ID (PK) field in the model class
        :param already_exists_exception_class: Exception class for already exists error
        :param not_found_exception_class: Exception class for not found error
        """
        self.session = session
        self.model = model_class
        self.id_field = id_field
        self.already_exists_exception_class = already_exists_exception_class
        self.not_found_exception_class = not_found_exception_class

    @abstractmethod
    def map_model_to_dto(self, model: Any) -> Any:  # noqa
        """Map DBModel to DTO."""
        raise NotImplementedError

    @abstractmethod
    def map_dto_to_model(self, dto: Any) -> Any:  # noqa
        """Map DTO to DBModel."""
        raise NotImplementedError

    async def get_by_id(self, entity_id: IDType) -> DTO | None:
        """Get an entity by ID."""
        try:
            entity = await self.session.get_one(self.model, entity_id)
            return self.map_model_to_dto(entity) if entity else None
        except NoResultFound:
            return None

    async def get_all(self) -> list[DTO]:
        """Get all entities."""
        resp = await self.session.execute(select(self.model))
        entities = resp.scalars().all()
        return [self.map_model_to_dto(entity) for entity in entities]

    async def create(self, dto: DTO) -> DTO:
        """Create a new entity."""
        entity = self.map_dto_to_model(dto)
        existed = await self.get_by_id(getattr(entity, self.id_field))
        if existed:
            raise self.already_exists_exception_class(
                f"{self.model.__name__} with ID {getattr(entity, self.id_field)} already exists",
            )
        # Use merge instead of add to handle existing nested objects
        entity = await self.session.merge(entity)
        try:
            await self.session.flush()
            res: DTO = self.map_model_to_dto(entity)
            return res
        except IntegrityError as e:
            await self.session.rollback()
            raise self.already_exists_exception_class(
                f"{self.model.__name__} with ID {getattr(entity, self.id_field)} already exists",
            ) from e

    async def update(self, dto: DTO) -> DTO:
        """Update an existing entity."""
        entity = self.map_dto_to_model(dto)
        update_values = self._get_update_values_dict(entity)
        resp = await self.session.execute(
            sa_update(self.model)
            .where(getattr(self.model, self.id_field) == getattr(entity, self.id_field))
            .values(**update_values),
        )
        await self.session.flush()
        if resp.rowcount == 0:
            raise self.not_found_exception_class(
                f"{self.model.__name__} with ID {getattr(entity, self.id_field)} not found for update",
            )
        return dto

    async def delete(self, entity_id: IDType) -> None:
        """Delete an entity by ID."""
        try:
            entity = await self.session.get_one(self.model, entity_id)
            await self.session.delete(entity)
            await self.session.flush()
        except NoResultFound:
            raise self.not_found_exception_class(f"{self.model.__name__} with ID {entity_id} not found for deletion")

    def _get_update_values_dict(self, db_model: DBModel) -> dict[str, Any]:
        """Get a dictionary of values from the DB model."""
        values = {column.name: getattr(db_model, column.name) for column in db_model.__table__.columns}
        del values[self.id_field]
        del values["creation_date"]

        return values
