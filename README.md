# Student Result Management System

A console-based Python application to manage student results using SQLite database. Supports full CRUD operations with automatic grade calculation.

## Features
- Add students with marks for 5 subjects
- View all students sorted by percentage
- Search student by name or roll number
- Update existing student marks
- Delete student records
- Auto-calculates Total, Percentage, and Grade

## Grade Scale
| Percentage | Grade |
|------------|-------|
| 90 - 100   | A+    |
| 80 - 89    | A     |
| 70 - 79    | B     |
| 60 - 69    | C     |
| 50 - 59    | D     |
| Below 50   | F     |

## Tech Stack
- Python 3.x
- SQLite3 (built-in)

## How to Run

```bash
python main.py
```

No external dependencies required — uses Python's built-in `sqlite3` module.

## Project Structure
```
student-result-management/
├── main.py        # Entry point, menu interface
├── database.py    # DB connection and initialization
├── student.py     # CRUD operations & grade logic
└── README.md
```

## Author
Rajesh Prajapat  
GitHub: github.com/rajeshprajapat
