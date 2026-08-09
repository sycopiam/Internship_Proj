# ServiceFlow - Database Schema Documentation

## Database Technology
- **Database Engine**: SQLite (`serviceflow.db`)
- **ORM**: SQLAlchemy
- **Schema Management**: Auto-migrated on startup via `Base.metadata.create_all()`

## Entity Relationship Diagram (ERD)

```
+------------------------------------+          +------------------------------------+
|               users                |          |              tickets               |
+------------------------------------+          +------------------------------------+
| id             INTEGER (PK)        |<---------| id             INTEGER (PK)        |
| name           VARCHAR(100)        |  creator | title          VARCHAR(200)        |
| email          VARCHAR(120) UNIQUE |          | description    TEXT                |
| password_hash  VARCHAR(200)        |          | category       VARCHAR(50)         |
| role           VARCHAR(20)         |          | priority       VARCHAR(20)         |
| created_at     DATETIME            |          | status         VARCHAR(30)         |
+------------------------------------+          | user_id        INTEGER (FK -> users)|
                                     |<---------| assigned_to    INTEGER (FK -> users)|
                                       assignee | created_at     DATETIME            |
                                                | updated_at     DATETIME            |
                                                +------------------------------------+
```

## Table Specifications

### 1. `users`
Stores user profile information, authentication credentials, and system roles.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique user identifier |
| `name` | VARCHAR(100) | NOT NULL | User's full name |
| `email` | VARCHAR(120) | NOT NULL, UNIQUE, INDEX | Email address used for login |
| `password_hash` | VARCHAR(200) | NOT NULL | Bcrypt salted password hash |
| `role` | VARCHAR(20) | DEFAULT 'user' | Access control role (`user` or `admin`) |
| `created_at` | DATETIME | DEFAULT UTC NOW | Timestamp of account registration |

### 2. `tickets`
Stores IT incident/service request records submitted by users.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique ticket reference number |
| `title` | VARCHAR(200) | NOT NULL | Concise description of the issue |
| `description` | TEXT | NOT NULL | Detailed explanation of the issue |
| `category` | VARCHAR(50) | NOT NULL, DEFAULT 'Other' | Category (`Hardware`, `Software`, `Network`, `Account`, `Email`, `Other`) |
| `priority` | VARCHAR(20) | NOT NULL, DEFAULT 'Medium' | Impact priority (`Low`, `Medium`, `High`, `Critical`) |
| `status` | VARCHAR(30) | NOT NULL, DEFAULT 'Open' | Lifecycle status (`Open`, `Assigned`, `In Progress`, `Resolved`, `Closed`) |
| `user_id` | INTEGER | FOREIGN KEY (`users.id`) | User ID of creator |
| `assigned_to` | INTEGER | FOREIGN KEY (`users.id`), NULLABLE | User ID of assigned IT admin |
| `created_at` | DATETIME | DEFAULT UTC NOW | Timestamp when ticket was created |
| `updated_at` | DATETIME | DEFAULT UTC NOW | Timestamp of last modification |
