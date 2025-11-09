# Development Practices

This document outlines the coding standards and practices to follow in this project.

## Clean Code Principles

### Code Quality
- Write self-documenting code with clear, descriptive names
- Keep functions small and focused on a single responsibility
- Use meaningful variable and function names that express intent
- Avoid deep nesting - prefer early returns and guard clauses
- Remove dead code and unused imports regularly

### Code Organization
- Follow the Single Responsibility Principle (SRP)
- Apply the DRY principle - Don't Repeat Yourself
- Use consistent formatting and indentation
- Group related functionality together
- Separate concerns clearly between layers

## API First Development

### Design Principles
- Define APIs before implementation begins
- Use OpenAPI/Swagger specifications for REST APIs
- Design APIs from the consumer's perspective
- Ensure APIs are consistent, predictable, and well-documented
- Version APIs properly to maintain backward compatibility

### API Guidelines
- Follow RESTful conventions and HTTP standards
- Use clear, descriptive resource names and endpoints
- Implement proper error handling with meaningful status codes
- Include comprehensive documentation and examples
- Design for extensibility and future requirements

### Contract-First Approach
- Create API contracts as the source of truth
- Generate client SDKs and server stubs from specifications
- Use contract testing to ensure API compliance
- Mock APIs early for parallel development
- Validate implementations against contracts

## Design Patterns

### Recommended Patterns
- **Repository Pattern** - For data access abstraction
- **Factory Pattern** - For object creation
- **Observer Pattern** - For event handling
- **Strategy Pattern** - For algorithm selection
- **Dependency Injection** - For loose coupling

### Pattern Guidelines
- Use patterns to solve actual problems, not for complexity's sake
- Prefer composition over inheritance
- Program to interfaces, not implementations
- Apply SOLID principles consistently

## Test-Driven Development (TDD)

### TDD Cycle
1. **Red** - Write a failing test first
2. **Green** - Write minimal code to make the test pass
3. **Refactor** - Improve code while keeping tests green

### Testing Guidelines
- Write tests before implementation code
- Keep tests simple, focused, and fast
- Use descriptive test names that explain the behavior
- Test behavior, not implementation details
- Maintain high test coverage for critical paths

## Anti-Patterns to Avoid

### Code Smells
- **God Objects** - Classes that do too much
- **Long Parameter Lists** - Use objects or builders instead
- **Magic Numbers** - Use named constants
- **Duplicate Code** - Extract common functionality
- **Large Classes/Methods** - Break into smaller units

### Architecture Anti-Patterns
- **Spaghetti Code** - Tangled, unstructured code
- **Big Ball of Mud** - Lack of clear architecture
- **Vendor Lock-in** - Over-dependence on specific technologies
- **Premature Optimization** - Optimizing before measuring

### Common Mistakes
- Ignoring error handling
- Not validating inputs
- Hardcoding configuration values
- Mixing business logic with presentation
- Not considering edge cases

## Code Documentation

### Docstring Standards
- Use Python docstrings for all classes, methods, and functions
- Follow Google or NumPy docstring format consistently
- Document parameters, return values, and exceptions
- Include usage examples for complex functions
- Keep docstrings concise but comprehensive

### Django-Specific Documentation
```python
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user accounts.
    
    Provides CRUD operations for user management with proper
    authentication and permission checks.
    
    Endpoints:
        GET /api/users/ - List all users
        POST /api/users/ - Create new user
        GET /api/users/{id}/ - Retrieve user details
        PUT /api/users/{id}/ - Update user
        DELETE /api/users/{id}/ - Delete user
    """
    
def calculate_total_price(items, discount=0):
    """
    Calculate total price with optional discount.
    
    Args:
        items (list): List of item dictionaries with 'price' key
        discount (float, optional): Discount percentage (0-100). Defaults to 0.
        
    Returns:
        Decimal: Total price after discount
        
    Raises:
        ValueError: If discount is not between 0 and 100
        
    Example:
        >>> items = [{'price': 10.00}, {'price': 20.00}]
        >>> calculate_total_price(items, discount=10)
        Decimal('27.00')
    """
```

### API Documentation
- Use DRF's built-in schema generation
- Document all API endpoints with clear descriptions
- Include request/response examples
- Document authentication requirements
- Specify required vs optional parameters

### Code Comments
- Use inline comments sparingly for complex logic
- Explain "why" not "what" in comments
- Update comments when code changes
- Remove outdated or obvious comments
- Use TODO comments for future improvements

## UML Documentation

### Diagram Standards
- Use UML diagrams to document system architecture and design
- Create diagrams using Mermaid syntax for version control compatibility
- Include diagrams in markdown documentation files
- Keep diagrams up-to-date with code changes

### Required UML Diagrams
- **Class Diagrams**: Document Django models and their relationships
- **Sequence Diagrams**: Show API request/response flows
- **Use Case Diagrams**: Document user interactions with the system
- **Component Diagrams**: Show system architecture and dependencies

### Mermaid Examples
```mermaid
classDiagram
    class Initiative {
        +String name
        +String description
        +Date start_date
        +Date end_date
        +String type
        +get_children()
        +add_team_member()
    }
    
    class Person {
        +String first_name
        +String last_name
        +String email
        +get_initiatives()
    }
    
    Initiative ||--o{ Initiative : parent/child
    Initiative }o--|| Person : coordinator
    Initiative }o--o{ Person : team_members
```

### Documentation Integration
- Include UML diagrams in design documents
- Reference diagrams in code comments when helpful
- Use diagrams to explain complex business logic
- Update diagrams during code reviews