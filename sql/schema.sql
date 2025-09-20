-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('ADMIN', 'FIELD_WORKER', 'USER')),
    is_active BOOLEAN DEFAULT TRUE,
    is_approved BOOLEAN DEFAULT FALSE,
    phone VARCHAR(15),
    address TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert default admin safely
INSERT INTO users (username, email, hashed_password, role, is_active, is_approved)
VALUES ('admin', 'admin@fieldops.com', '$2b$12$KIXyZDy6zjJ1JQqC1vR6eOcP7J5lKJ3L8d9X0a1b2c3d4e5f6g7h8i9j0k', 'ADMIN', TRUE, TRUE)
ON CONFLICT (username) DO NOTHING;

-- Tasks Table
CREATE TABLE IF NOT EXISTS service_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    field_worker_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    urgency VARCHAR(10) CHECK (urgency IN ('LOW', 'MEDIUM', 'HIGH')) DEFAULT 'MEDIUM',
    status VARCHAR(20) CHECK (status IN ('PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP NULL,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5) NULL
);

-- Task Proofs Table
CREATE TABLE IF NOT EXISTS task_proofs (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES service_requests(id) ON DELETE CASCADE,
    image_path TEXT,
    notes TEXT,
    uploaded_at TIMESTAMP DEFAULT NOW()
);
