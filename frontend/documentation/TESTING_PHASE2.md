# Testing Phase 2: Initiatives Module

This guide will help you test all Phase 2 features using the mock API.

## Prerequisites

1. **Start the Mock API Server**
   ```bash
   cd frontend
   npm run mock-api
   ```

2. **Start the Frontend Dev Server** (in another terminal)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Login Credentials**
   - Username: `admin`
   - Password: `admin123`

## Test Scenarios

### 1. Authentication
- [ ] Navigate to http://localhost:5173/login
- [ ] Enter credentials and login
- [ ] Verify redirect to dashboard
- [ ] Check user menu shows "Admin User"

### 2. Initiative List View
- [ ] Navigate to "Initiatives" from sidebar
- [ ] Verify 5 initiatives are displayed
- [ ] Test search functionality
- [ ] Test type filter (Program, Project, Event)
- [ ] Test pagination
- [ ] Click on an initiative card to view details

### 3. Initiative Detail View
- [ ] View initiative details
- [ ] Verify all fields are displayed correctly
- [ ] Check team members list
- [ ] Check students list
- [ ] View hierarchy (if parent exists)
- [ ] Click "Edit" button (if you have permission)
- [ ] Click "Delete" button and cancel

### 4. Create Initiative
- [ ] Click "Create Initiative" button
- [ ] Fill in all required fields:
  - Name
  - Description
  - Type (select from dropdown)
  - Start Date
  - Coordinator (select from autocomplete)
- [ ] Fill in optional fields:
  - End Date
  - Parent Initiative
  - Team Members
  - Students
  - Organizational Groups
- [ ] Click "Create"
- [ ] Verify success message
- [ ] Verify redirect to initiatives list

### 5. Edit Initiative
- [ ] Open an initiative detail view
- [ ] Click "Edit" button
- [ ] Modify some fields
- [ ] Click "Update"
- [ ] Verify success message
- [ ] Verify changes are reflected

### 6. Team Member Management
- [ ] Open an initiative detail view
- [ ] In Team Members card, click "Add Member"
- [ ] Select a person from dropdown
- [ ] Click "Add"
- [ ] Verify member appears in list
- [ ] Click delete icon on a member
- [ ] Verify member is removed

### 7. Student Management
- [ ] Open an initiative detail view
- [ ] In Students card, click "Add Student"
- [ ] Select a student from dropdown
- [ ] Click "Add"
- [ ] Verify student appears in list
- [ ] Click delete icon on a student
- [ ] Verify student is removed

### 8. Initiative Hierarchy
- [ ] Open an initiative that has a parent (e.g., ID 2 or 5)
- [ ] Scroll to hierarchy section
- [ ] Verify tree structure is displayed
- [ ] Click expand/collapse buttons
- [ ] Click on a node to navigate

### 9. Bulk Import - CSV
- [ ] Navigate to "Initiatives" > "Import" button
- [ ] Select "CSV" tab
- [ ] Click "Download Template"
- [ ] Verify CSV file downloads
- [ ] Upload a CSV file (use template)
- [ ] Verify upload progress
- [ ] Check import results

### 10. Bulk Import - ZIP
- [ ] Navigate to import page
- [ ] Select "ZIP" tab
- [ ] Upload a ZIP file
- [ ] Verify upload progress
- [ ] Check import results

### 11. Failed Imports
- [ ] Navigate to "View Failed Imports" link
- [ ] Verify failed imports are listed
- [ ] Expand an import to see details
- [ ] View error messages
- [ ] Click "Retry" button
- [ ] Click "Delete" button

### 12. Search and Filters
- [ ] On initiatives list, enter search text
- [ ] Verify results update
- [ ] Clear search
- [ ] Open filters panel
- [ ] Select a type filter
- [ ] Apply filters
- [ ] Verify filtered results
- [ ] Clear all filters

### 13. Pagination
- [ ] On initiatives list, change page size
- [ ] Navigate to next page
- [ ] Navigate to previous page
- [ ] Jump to specific page

### 14. Coordinator Change History
- [ ] Open initiative detail (ID 2 has history)
- [ ] Scroll to coordinator changes section
- [ ] Verify timeline is displayed
- [ ] Check change details
- [ ] Verify dates and users

### 15. Permissions
- [ ] Login as different users:
  - `maria.silva` / `senha123` (staff)
  - `joao.santos` / `senha123` (regular)
- [ ] Verify action buttons appear/disappear based on permissions
- [ ] Try to access restricted routes

### 16. Responsive Design
- [ ] Resize browser window
- [ ] Test on mobile viewport (DevTools)
- [ ] Verify sidebar collapses
- [ ] Check card layouts adapt
- [ ] Test forms on small screens

### 17. Internationalization
- [ ] Click language switcher in header
- [ ] Switch to Portuguese (pt-BR)
- [ ] Verify all text is translated
- [ ] Switch back to English
- [ ] Verify translations work

### 18. Error Handling
- [ ] Stop the mock API server
- [ ] Try to load initiatives list
- [ ] Verify error message appears
- [ ] Restart mock API
- [ ] Verify data loads

### 19. Loading States
- [ ] Refresh page while on initiatives list
- [ ] Verify loading spinner appears
- [ ] Wait for data to load
- [ ] Verify smooth transition

### 20. Navigation
- [ ] Use breadcrumbs to navigate
- [ ] Use browser back button
- [ ] Use sidebar menu
- [ ] Verify all navigation works correctly

## Expected Results

All tests should pass with:
- ✅ No console errors
- ✅ Smooth transitions
- ✅ Proper loading states
- ✅ Clear error messages
- ✅ Responsive layouts
- ✅ Correct translations
- ✅ Permission enforcement

## Common Issues

### Mock API Not Running
**Symptom**: "Failed to connect" errors  
**Solution**: Start mock API with `npm run mock-api`

### Port Already in Use
**Symptom**: "Port 8000 already in use"  
**Solution**: Kill existing process or change port

### Authentication Issues
**Symptom**: Redirected to login repeatedly  
**Solution**: Clear browser localStorage and login again

### Data Not Updating
**Symptom**: Changes don't appear  
**Solution**: Mock API uses in-memory storage, restart to reset

## Mock API Endpoints

The mock API provides these endpoints:

### Authentication
- `POST /auth/login` - Login
- `POST /auth/logout` - Logout
- `GET /auth/me` - Current user
- `POST /auth/token/refresh` - Refresh token

### Initiatives
- `GET /api/initiatives` - List initiatives
- `POST /api/initiatives` - Create initiative
- `GET /api/initiatives/:id` - Get initiative
- `PUT /api/initiatives/:id` - Update initiative
- `DELETE /api/initiatives/:id` - Delete initiative
- `GET /api/initiatives/:id/hierarchy` - Get hierarchy
- `GET /api/initiatives/:id/children` - Get children
- `POST /api/initiatives/:id/team-members` - Add team member
- `DELETE /api/initiatives/:id/team-members/:personId` - Remove team member
- `POST /api/initiatives/:id/students` - Add student
- `DELETE /api/initiatives/:id/students/:personId` - Remove student
- `POST /api/initiatives/import/csv` - Import CSV
- `POST /api/initiatives/import/zip` - Import ZIP
- `GET /api/initiatives/failed-imports` - List failed imports
- `POST /api/initiatives/failed-imports/:id/retry` - Retry import
- `DELETE /api/initiatives/failed-imports/:id` - Delete failed import
- `GET /api/initiatives/:id/coordinator-changes` - Get coordinator changes
- `GET /api/initiatives/statistics` - Get statistics

## Test Data

The mock API includes:
- 3 test users (admin, maria.silva, joao.santos)
- 5 initiatives (2 programs, 2 projects, 1 event)
- 8 people
- 3 organizational groups
- 2 failed imports
- 1 coordinator change record

## Reporting Issues

If you find any issues during testing:
1. Note the steps to reproduce
2. Check browser console for errors
3. Check mock API logs
4. Document expected vs actual behavior
5. Create a bug report with details

## Next Steps

After completing Phase 2 testing:
1. Review any issues found
2. Fix critical bugs
3. Proceed to Phase 3: Scholarships Module
4. Plan comprehensive testing in Phase 6

---

**Happy Testing!** 🧪
