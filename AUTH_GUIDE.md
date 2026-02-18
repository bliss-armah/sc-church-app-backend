# Authentication & Authorization Guide

Complete guide for the user authentication and role-based access control system.

## 🔐 Overview

The CMS now includes a complete authentication system with:

- **JWT-based authentication**
- **Role-based access control** (Admin and User roles)
- **Password management** (change password, reset password)
- **Default admin account** created on first run

## 👥 User Roles

### Admin Role

- **Full access** to everything
- Can create, update, and delete users
- Can manage all members
- Can reset user passwords
- Cannot delete the last admin user

### User Role (Sub-users)

- Can **create and manage members**
- Can view all members
- **Cannot** manage other users
- **Cannot** access admin endpoints
- Must change password on first login

## 🚀 Getting Started

### Default Admin Account

On first run, a default admin account is automatically created:

```
Username: admin
Email: admin@cms.local
Password: Admin@123
```

**⚠️ IMPORTANT:** Change this password immediately after first login!

### First Login

1. **Login** with default credentials
2. **Change password** (required on first login)
3. **Create sub-users** for your team

## 📝 API Endpoints

### Authentication Endpoints (Public)

#### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "Admin@123"
}
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "admin@cms.local",
    "username": "admin",
    "full_name": "System Administrator",
    "role": "admin",
    "is_active": true,
    "must_change_password": true,
    ...
  }
}
```

#### Get Current User

```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

#### Change Password

```http
POST /api/v1/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "Admin@123",
  "new_password": "NewSecure@Pass123"
}
```

### User Management Endpoints (Admin Only)

#### Create User

```http
POST /api/v1/users
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "email": "john@example.com",
  "username": "john_doe",
  "full_name": "John Doe",
  "password": "TempPass@123",
  "role": "user"
}
```

**Password Requirements:**

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

**Username Requirements:**

- 3-100 characters
- Alphanumeric with hyphens and underscores
- Automatically converted to lowercase

#### List Users

```http
GET /api/v1/users?page=1&page_size=20&role=user&is_active=true
Authorization: Bearer <admin_token>
```

#### Get User by ID

```http
GET /api/v1/users/{user_id}
Authorization: Bearer <admin_token>
```

#### Update User

```http
PUT /api/v1/users/{user_id}
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "full_name": "John Smith",
  "is_active": false
}
```

#### Reset User Password

```http
POST /api/v1/users/{user_id}/reset-password
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "new_password": "NewTemp@Pass123"
}
```

**Note:** User will be required to change password on next login.

#### Delete User

```http
DELETE /api/v1/users/{user_id}
Authorization: Bearer <admin_token>
```

### Member Endpoints (Authenticated Users)

All member endpoints now require authentication:

```http
GET /api/v1/members
Authorization: Bearer <access_token>
```

Both admin and regular users can:

- Create members
- View members
- Update members
- Delete members

## 🔑 Using Authentication

### In API Docs (Swagger)

1. Go to http://localhost:8000/docs
2. Click the **"Authorize"** button (lock icon)
3. Enter username and password
4. Click **"Authorize"**
5. All requests will now include the token

### In Code (JavaScript/TypeScript)

```javascript
// Login
const loginResponse = await fetch("http://localhost:8000/api/v1/auth/login", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    username: "admin",
    password: "Admin@123",
  }),
});

const { access_token, user } = await loginResponse.json();

// Store token
localStorage.setItem("access_token", access_token);

// Use token in subsequent requests
const membersResponse = await fetch("http://localhost:8000/api/v1/members", {
  headers: {
    Authorization: `Bearer ${access_token}`,
  },
});
```

### In cURL

```bash
# Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}' \
  | jq -r '.access_token')

# Use token
curl http://localhost:8000/api/v1/members \
  -H "Authorization: Bearer $TOKEN"
```

## 🔄 Typical Workflows

### Admin Creates a Sub-User

1. **Admin logs in**

   ```http
   POST /api/v1/auth/login
   ```

2. **Admin creates user**

   ```http
   POST /api/v1/users
   {
     "email": "staff@church.com",
     "username": "staff_member",
     "full_name": "Staff Member",
     "password": "TempPass@123",
     "role": "user"
   }
   ```

3. **Share credentials** with the new user

### Sub-User First Login

1. **User logs in** with temporary password

   ```http
   POST /api/v1/auth/login
   ```

2. **Response shows** `must_change_password: true`

3. **User changes password**

   ```http
   POST /api/v1/auth/change-password
   {
     "current_password": "TempPass@123",
     "new_password": "MySecure@Pass456"
   }
   ```

4. **User can now** manage members

### Admin Resets User Password

1. **Admin resets password**

   ```http
   POST /api/v1/users/{user_id}/reset-password
   {
     "new_password": "NewTemp@789"
   }
   ```

2. **User must change** password on next login

## 🛡️ Security Features

### Password Security

- Passwords hashed with bcrypt
- Strong password requirements enforced
- Force password change on first login
- Force password change after admin reset

### Token Security

- JWT tokens with expiration (24 hours default)
- Tokens include user ID, username, and role
- Tokens verified on every protected request

### Role-Based Access

- Admin-only endpoints protected
- User role checked on each request
- Cannot delete last admin user

### Account Security

- Soft delete (data retained)
- Account deactivation
- Last login tracking

## ⚙️ Configuration

### JWT Settings (.env)

```env
# Generate with: openssl rand -hex 32
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
```

### Generate Secure Secret Key

```bash
openssl rand -hex 32
```

## 🧪 Testing Authentication

### Test Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin@123"}'
```

### Test Protected Endpoint

```bash
# Without token (should fail)
curl http://localhost:8000/api/v1/members

# With token (should succeed)
curl http://localhost:8000/api/v1/members \
  -H "Authorization: Bearer <your_token>"
```

### Test Admin Endpoint

```bash
# As regular user (should fail)
curl http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer <user_token>"

# As admin (should succeed)
curl http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer <admin_token>"
```

## 📊 Database Schema

### Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- 'admin' or 'user'
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    must_change_password BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    last_login TIMESTAMP
);
```

## 🚨 Common Issues

### "Could not validate credentials"

- Token expired (login again)
- Invalid token format
- Token not included in request

### "Admin privileges required"

- User role trying to access admin endpoint
- Use admin account for user management

### "User account is inactive"

- Account has been deactivated
- Contact admin to reactivate

### "Cannot delete the last admin user"

- System requires at least one admin
- Create another admin first

## 🎯 Best Practices

1. **Change default admin password** immediately
2. **Use strong passwords** for all accounts
3. **Generate secure SECRET_KEY** for production
4. **Rotate tokens** regularly (adjust expiration time)
5. **Deactivate users** instead of deleting when possible
6. **Monitor last_login** for inactive accounts
7. **Use HTTPS** in production
8. **Store tokens securely** (httpOnly cookies recommended)

## 🔮 Future Enhancements

Potential additions:

- Refresh tokens
- Password reset via email
- Two-factor authentication (2FA)
- Session management
- Audit logging
- Password history
- Account lockout after failed attempts
- OAuth2 integration

## 📚 Related Documentation

- [API Examples](EXAMPLES.md) - Request/response examples
- [Extension Guide](EXTENSION_GUIDE.md) - Adding new features
- [Architecture](ARCHITECTURE.md) - System design
