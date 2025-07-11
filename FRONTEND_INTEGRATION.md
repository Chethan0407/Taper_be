# Frontend Integration Guide

## Users Endpoint for Assignment Dropdowns

### Overview
The `/api/v1/users/` endpoint provides user data for frontend assignment dropdowns with optional role filtering and pagination support.

### Authentication
All endpoints require JWT authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

### API Endpoints

#### 1. List Users (with filtering)
```
GET /api/v1/users/
```

**Query Parameters:**
- `role` (optional): Filter by role ("admin", "engineer", "pm")
- `is_active` (optional): Filter by active status (true/false)
- `skip` (optional): Number of records to skip for pagination (default: 0)
- `limit` (optional): Number of records to return (default: 100, max: 1000)

**Response:**
```json
[
  {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "engineer",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2025-07-10T00:57:48.682234+05:30",
    "updated_at": "2025-07-10T00:57:48.682234+05:30"
  }
]
```

#### 2. Get Specific User
```
GET /api/v1/users/{user_id}
```

**Response:** Same as list users but single object

#### 3. Get Current User Profile
```
GET /api/v1/users/me/profile
```

**Response:** Current user's full profile information

### Frontend Implementation Examples

#### React Hook for User Management
```javascript
import { useState, useEffect } from 'react';

const useUsers = (filters = {}) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchUsers = async (params = {}) => {
    setLoading(true);
    try {
      const queryParams = new URLSearchParams({
        ...filters,
        ...params
      });
      
      const response = await fetch(`/api/v1/users/?${queryParams}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) throw new Error('Failed to fetch users');
      
      const data = await response.json();
      setUsers(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [filters]);

  return { users, loading, error, refetch: fetchUsers };
};
```

#### Assignment Dropdown Component
```javascript
import React, { useState, useEffect } from 'react';

const AssignmentDropdown = ({ 
  value, 
  onChange, 
  roleFilter = null, 
  placeholder = "Select user..." 
}) => {
  const { users, loading, error } = useUsers({
    role: roleFilter,
    is_active: true
  });

  if (loading) return <div>Loading users...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <select 
      value={value || ''} 
      onChange={(e) => onChange(e.target.value)}
      className="form-select"
    >
      <option value="">{placeholder}</option>
      {users.map(user => (
        <option key={user.id} value={user.id}>
          {user.full_name || user.email} ({user.role})
        </option>
      ))}
    </select>
  );
};
```

#### User Assignment in Checklist Items
```javascript
const ChecklistItemAssignment = ({ itemId, currentAssignee, onAssign }) => {
  const [assignee, setAssignee] = useState(currentAssignee);

  const handleAssignment = async (userId) => {
    try {
      const response = await fetch(`/api/v1/checklists/items/${itemId}/assign`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_id: userId })
      });
      
      if (response.ok) {
        setAssignee(userId);
        onAssign(userId);
      }
    } catch (error) {
      console.error('Assignment failed:', error);
    }
  };

  return (
    <div className="assignment-section">
      <label>Assigned to:</label>
      <AssignmentDropdown
        value={assignee}
        onChange={handleAssignment}
        roleFilter="engineer"
        placeholder="Assign to engineer..."
      />
    </div>
  );
};
```

#### User Management Table
```javascript
const UserManagementTable = () => {
  const [filters, setFilters] = useState({});
  const [pagination, setPagination] = useState({ skip: 0, limit: 20 });
  const { users, loading, error, refetch } = useUsers({ ...filters, ...pagination });

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    setPagination({ skip: 0, limit: 20 }); // Reset pagination
  };

  const handlePageChange = (newSkip) => {
    setPagination(prev => ({ ...prev, skip: newSkip }));
  };

  return (
    <div className="user-management">
      <div className="filters">
        <select 
          onChange={(e) => handleFilterChange({ role: e.target.value })}
          className="form-select"
        >
          <option value="">All Roles</option>
          <option value="admin">Admin</option>
          <option value="engineer">Engineer</option>
          <option value="pm">Project Manager</option>
        </select>
        
        <select 
          onChange={(e) => handleFilterChange({ is_active: e.target.value })}
          className="form-select"
        >
          <option value="">All Status</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>

      {loading && <div>Loading...</div>}
      {error && <div>Error: {error}</div>}
      
      <table className="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.id}>
              <td>{user.full_name || 'N/A'}</td>
              <td>{user.email}</td>
              <td>{user.role}</td>
              <td>{user.is_active ? 'Active' : 'Inactive'}</td>
              <td>{new Date(user.created_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="pagination">
        <button 
          onClick={() => handlePageChange(Math.max(0, pagination.skip - pagination.limit))}
          disabled={pagination.skip === 0}
        >
          Previous
        </button>
        <span>Page {Math.floor(pagination.skip / pagination.limit) + 1}</span>
        <button 
          onClick={() => handlePageChange(pagination.skip + pagination.limit)}
          disabled={users.length < pagination.limit}
        >
          Next
        </button>
      </div>
    </div>
  );
};
```

### Error Handling

#### Common Error Responses
```javascript
// 401 Unauthorized
{
  "detail": "Not authenticated"
}

// 404 Not Found
{
  "detail": "User not found"
}

// 422 Validation Error
{
  "detail": [
    {
      "loc": ["query", "limit"],
      "msg": "ensure this value is less than or equal to 1000",
      "type": "value_error.any_str.max_length"
    }
  ]
}
```

#### Error Handling in Components
```javascript
const handleApiError = (error) => {
  if (error.status === 401) {
    // Redirect to login
    window.location.href = '/login';
  } else if (error.status === 404) {
    // Show not found message
    setError('User not found');
  } else {
    // Show generic error
    setError('An error occurred. Please try again.');
  }
};
```

### Best Practices

1. **Caching**: Cache user lists to avoid repeated API calls
2. **Debouncing**: Debounce search/filter inputs to avoid excessive API calls
3. **Loading States**: Always show loading indicators during API calls
4. **Error Boundaries**: Implement error boundaries for graceful error handling
5. **Accessibility**: Ensure dropdowns are keyboard accessible and screen reader friendly
6. **Validation**: Validate user IDs before making assignment API calls

### Security Considerations

1. **Token Management**: Store JWT tokens securely (httpOnly cookies preferred)
2. **Role-based UI**: Hide assignment options based on user permissions
3. **Input Validation**: Validate all user inputs before sending to API
4. **CSRF Protection**: Implement CSRF tokens for state-changing operations
5. **Rate Limiting**: Respect API rate limits and implement retry logic

### Testing

#### Unit Tests
```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import AssignmentDropdown from './AssignmentDropdown';

test('renders user options correctly', async () => {
  const mockUsers = [
    { id: 1, email: 'user1@example.com', full_name: 'User 1', role: 'engineer' },
    { id: 2, email: 'user2@example.com', full_name: 'User 2', role: 'engineer' }
  ];
  
  // Mock the API call
  global.fetch = jest.fn(() =>
    Promise.resolve({
      ok: true,
      json: () => Promise.resolve(mockUsers)
    })
  );

  render(<AssignmentDropdown value="" onChange={() => {}} />);
  
  await screen.findByText('User 1 (engineer)');
  expect(screen.getByText('User 2 (engineer)')).toBeInTheDocument();
});
```

#### Integration Tests
```javascript
test('assigns user to checklist item', async () => {
  const mockAssignResponse = { success: true };
  global.fetch = jest.fn()
    .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockUsers) })
    .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve(mockAssignResponse) });

  render(<ChecklistItemAssignment itemId={1} currentAssignee={null} onAssign={() => {}} />);
  
  const dropdown = screen.getByRole('combobox');
  fireEvent.change(dropdown, { target: { value: '1' } });
  
  expect(global.fetch).toHaveBeenCalledWith(
    '/api/v1/checklists/items/1/assign',
    expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ user_id: '1' })
    })
  );
});
``` 