from fastapi import FastAPI, HTTPException

from app.schemas import Student, StudentCreate, StudentUpdate

app = FastAPI(title="Student Management API")

students: dict[int, Student] = {
    student.id: student for student in [
        Student(id=1, name="Alice", age=20, major="Computer Science"),
        Student(id=2, name="Bob", age=22, major="Mathematics"),
        Student(id=3, name="Charlie", age=21, major="Physics"), 
    ]
}
next_id = 4


@app.post("/students", response_model=Student, status_code=201)
def create_student(student: StudentCreate) -> Student:
    global next_id
    new_student = Student(id=next_id, **student.model_dump())
    students[next_id] = new_student
    next_id += 1
    return new_student


@app.get("/students", response_model=list[Student])
def list_students() -> list[Student]:
    return list(students.values())


@app.get("/students/{student_id}", response_model=Student)
def get_student(student_id: int) -> Student:
    student = students.get(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, student: StudentUpdate) -> Student:
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    updated_student = Student(id=student_id, **student.model_dump())
    students[student_id] = updated_student
    return updated_student


@app.delete("/students/{student_id}", status_code=204)
def delete_student(student_id: int) -> None:
    if student_id not in students:
        raise HTTPException(status_code=404, detail="Student not found")
    del students[student_id]
