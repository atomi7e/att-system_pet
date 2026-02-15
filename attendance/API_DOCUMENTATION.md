# API Documentation

## Base URL
```
http://localhost:8000/api/  (Development)
https://your-app.com/api/   (Production)
```

## Endpoints

### 1. GET /api/attendance/
Retrieve attendance records with optional filtering.

**Query Parameters:**
- `class_id` (optional): Filter by class ID
- `date` (optional): Filter by date (YYYY-MM-DD format)
- `student_id` (optional): Filter by student ID

**Example Request:**
```
GET /api/attendance/?class_id=1&date=2025-01-18
```

**Response:**
```json
[
    {
        "id": 1,
        "student": 1,
        "student_name": "Alice Johnson",
        "student_id": "S001",
        "class_enrolled": 1,
        "class_name": "Django REST Framework",
        "date": "2025-01-18",
        "status": "present",
        "notes": "",
        "marked_at": "2025-01-18T10:30:00Z"
    }
]
```

---

### 2. POST /api/attendance/mark/
Create or update an attendance record.

**Request Body (JSON):**
```json
{
    "student_id": 1,
    "class_id": 1,
    "date": "2025-01-18",
    "status": "present",
    "notes": "Optional notes"
}
```

**Status Values:**
- `"present"` - Student is present
- `"absent"` - Student is absent
- `"late"` - Student is late

**Response (201 Created or 200 OK):**
```json
{
    "id": 1,
    "student": 1,
    "student_name": "Alice Johnson",
    "student_id": "S001",
    "class_enrolled": 1,
    "class_name": "Django REST Framework",
    "date": "2025-01-18",
    "status": "present",
    "notes": "Optional notes",
    "marked_at": "2025-01-18T10:30:00Z"
}
```

**Error Responses:**
- `400 Bad Request`: Missing required fields or invalid data
- `404 Not Found`: Student or class not found

---

### 3. GET /api/attendance/{id}/
Retrieve a specific attendance record by ID.

**Example Request:**
```
GET /api/attendance/1/
```

**Response:**
```json
{
    "id": 1,
    "student": 1,
    "student_name": "Alice Johnson",
    "student_id": "S001",
    "class_enrolled": 1,
    "class_name": "Django REST Framework",
    "date": "2025-01-18",
    "status": "present",
    "notes": "",
    "marked_at": "2025-01-18T10:30:00Z"
}
```

---

### 4. PUT /api/attendance/{id}/
Update an existing attendance record.

**Request Body (JSON):**
```json
{
    "status": "late",
    "date": "2025-01-18",
    "notes": "Updated notes"
}
```

**Note:** All fields are optional. Only provided fields will be updated.

**Response:**
```json
{
    "id": 1,
    "student": 1,
    "student_name": "Alice Johnson",
    "student_id": "S001",
    "class_enrolled": 1,
    "class_name": "Django REST Framework",
    "date": "2025-01-18",
    "status": "late",
    "notes": "Updated notes",
    "marked_at": "2025-01-18T10:30:00Z"
}
```

---

### 5. DELETE /api/attendance/{id}/
Delete an attendance record.

**Example Request:**
```
DELETE /api/attendance/1/
```

**Response:**
- `204 No Content`: Successfully deleted

---

## Testing with Postman

### Setup
1. Create a new collection in Postman
2. Set base URL: `http://localhost:8000/api/`

### Test Cases

#### 1. Get All Attendance Records
- Method: GET
- URL: `{{base_url}}attendance/`
- Expected: 200 OK with array of attendance records

#### 2. Get Filtered Attendance
- Method: GET
- URL: `{{base_url}}attendance/?class_id=1&date=2025-01-18`
- Expected: 200 OK with filtered records

#### 3. Create Attendance Record
- Method: POST
- URL: `{{base_url}}attendance/mark/`
- Headers: `Content-Type: application/json`
- Body:
  ```json
  {
      "student_id": 1,
      "class_id": 1,
      "date": "2025-01-18",
      "status": "present"
  }
  ```
- Expected: 201 Created

#### 4. Get Specific Record
- Method: GET
- URL: `{{base_url}}attendance/1/`
- Expected: 200 OK with single record

#### 5. Update Record
- Method: PUT
- URL: `{{base_url}}attendance/1/`
- Headers: `Content-Type: application/json`
- Body:
  ```json
  {
      "status": "late",
      "notes": "Updated via API"
  }
  ```
- Expected: 200 OK with updated record

#### 6. Delete Record
- Method: DELETE
- URL: `{{base_url}}attendance/1/`
- Expected: 204 No Content

---

## Error Codes

- `200 OK`: Successful GET or PUT request
- `201 Created`: Successful POST request (new record created)
- `204 No Content`: Successful DELETE request
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Notes

- All dates must be in `YYYY-MM-DD` format
- Status must be one of: `"present"`, `"absent"`, or `"late"`
- A student can only have one attendance record per day (unique constraint)
- All timestamps are in UTC format

