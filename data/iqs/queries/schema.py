from typing import List

from pydantic import BaseModel, Field


class get_all_vehicle_names(BaseModel):
    """Retrieve a list of unique vehicle names. These will include vehicle make and model."""


class get_number_of_complaints(BaseModel):
    """Retrieve the total number of complaints (verbatims) in the database. Returns a single integer."""


class get_number_of_complaints_for_a_make_and_model(BaseModel):
    """Retrieve the total number of complaints (verbatims) for a particular vehicle make and model. Returns a count for each unique make and model combination."""

    make: str = Field(..., description="The make of a vehicle.")
    model: str = Field(..., description="The model of a vehicle.")


class get_number_of_complaints_for_a_make(BaseModel):
    """Retrieve the total number of complaints (verbatims) for only a particular vehicle make. Returns a single integer."""

    make: str = Field(..., description="The make of a vehicle.")


class get_number_of_complaints_for_a_model(BaseModel):
    """Retrieve the total number of complaints (verbatims) for only a particular vehicle model. Returns a single integer."""

    model: str = Field(..., description="The model of a vehicle.")


def get_tool_schemas() -> List[type[BaseModel]]:
    return [
        get_all_vehicle_names,
        get_number_of_complaints,
        get_number_of_complaints_for_a_make,
        get_number_of_complaints_for_a_model,
        get_number_of_complaints_for_a_make_and_model,
    ]
