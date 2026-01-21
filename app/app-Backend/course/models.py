from pydantic import BaseModel
from typing import Optional

class CourseCreate(BaseModel):
    title: str
    description: str
    category: str
    duration: str
    price: float
    teacher_id: str

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    duration: Optional[str] = None
    price: Optional[float] = None

class EnrollmentCreate(BaseModel):
    course_id: str
    student_id: str