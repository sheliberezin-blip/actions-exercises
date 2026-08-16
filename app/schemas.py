from pydantic import BaseModel, Field


class StudentBase(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=0)
    major: str


class StudentCreate(StudentBase):
    pass


class StudentUpdate(StudentBase):
    pass


class Student(StudentBase):
    id: int
