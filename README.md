# FMS Django Project

A Django REST API application for tracking League of Legends player statistics, match data, and providing blog functionality. The system integrates with Riot Games API and PandaScore API to collect and analyze player performance data.

## Features

- **Player Management**: Track League of Legends players with their summoner names, ranks, and social media links
- **Match Tracking**: Store and analyze match participation data with detailed statistics
- **Official Statistics**: Integration with PandaScore API for professional match data
- **User System**: Custom user authentication with role-based permissions
- **Blog System**: Post creation and management with content sanitization
- **Newsletter**: Email subscription functionality
- **Security**: Comprehensive security headers and JWT authentication

## Models Overview

### Core Models

- **User**: Custom user model with role-based permissions (USER, EDITOR, ADMIN)
- **Player**: League of Legends players with personal information and social media links
- **SummonerName**: Riot IDs associated with players, including rank information
- **Match**: Individual match records with game duration and timestamps
- **MatchParticipation**: Player performance in specific matches
- **PlayerOfficialStats**: Detailed professional match statistics from tournaments
- **Post**: Blog posts with author attribution and content sanitization
- **Newsletter**: Email subscription management

## API Endpoints

### Authentication
- `POST /api/register/` - User registration (public)
- `POST /api/login/` - User login (public)
- `POST /api/logout/` - User logout (authenticated)
- `GET /api/me/` - Current user information (authenticated)
- `GET /api/csrf/` - CSRF token (public)

### User Management
- `GET /api/users/` - List all users (admin only)
- `POST /api/users/create/` - Create new user (admin only)
- `GET /api/users/<nick>/` - User details (owner or admin)
- `PUT/PATCH /api/users/<nick>/edit/` - Edit user (owner or admin)
- `DELETE /api/users/<nick>/delete/` - Delete user (admin only)
- `GET /api/users/me/posts/` - Current user's posts (authenticated)

### Player Management
- `GET /api/players/` - List all players (public)
- `POST /api/players/create/` - Create new player (admin only)
- `GET /api/players/<nick>/` - Player details (authenticated)
- `GET /api/players/<nick>/ranks/` - Player rank information (public)
- `GET /api/players/<nick>/matches/` - Player match history (public, paginated)
- `GET /api/players/<nick>/official_stats/` - Aggregated official statistics (public)
- `GET /api/players/<nick>/official_stats/options/` - Available filter options (public)

### Blog System
- `GET /api/posts/` - List all posts (public, paginated)
- `POST /api/posts/create/` - Create new post (editor or admin)
- `PUT/PATCH /api/posts/<pk>/edit/` - Edit post (author or admin)
- `DELETE /api/posts/<pk>/delete/` - Delete post (author or admin)

### Newsletter
- `POST /api/newsletter/` - Subscribe to newsletter (public)

### External Data
- `GET /api/officialmatches/` - Fetch official matches from PandaScore API (public)

## Authentication & Security

### JWT Authentication
The application uses custom JWT authentication supporting both:
- Authorization header: `Bearer <token>`
- HTTP-only cookies for web applications

### Security Features
- **Content Security Policy (CSP)**: Different policies for development and production
- **Permissions Policy**: Comprehensive feature restrictions
- **Security Headers**: XSS protection, frame options, content type sniffing protection
- **HTTPS Enforcement**: Strict transport security in production
- **Content Sanitization**: HTML sanitization for blog posts using bleach

### Rate Limiting
- Anonymous users: 100 requests/hour
- Authenticated users: 500 requests/hour
- Login attempts: 5 attempts/minute
- Newsletter signup: 3 attempts/day
- PandaScore API: 60 requests/minute
- Post creation: 20 posts/hour

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- Redis (for production caching)

### Environment Variables
Create a `.env` file with the following variables:

```env
DJANGO_SECRET_KEY=your_secret_key_here
DEBUG=True
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DATABASE_URL=your_database_url (optional, overrides individual DB settings)
PANDASCORE_API_KEY=your_pandascore_api_key
UPSTASH_REDIS_REST_URL=your_redis_url (production only)
```

### Installation Steps

1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install django djangorestframework python-decouple psycopg2-binary
   pip install django-cors-headers python-dotenv dj-database-url
   pip install redis django-redis whitenoise bleach PyJWT
   ```

4. Set up database:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run development server:
   ```bash
   python manage.py runserver
   ```

## Key Features

### Player Statistics
The system provides comprehensive player analytics including:
- KDA (Kill/Death/Assist) ratios
- CS (Creep Score) per minute
- Damage per minute
- Kill participation percentage
- Gold participation percentage
- Vision score tracking

### Data Aggregation
Player statistics are aggregated with filtering options by:
- Champion
- Year
- Tournament
- Opposing team

### Caching
Production environment uses Redis for caching:
- Player filter options cached for 2 hours
- Aggregated statistics cached for 1 hour
- Development uses local memory caching

### Content Management
- Rich text support for blog posts with HTML sanitization
- Automatic link detection and safe rendering
- Author attribution and timestamp tracking

## Admin Interface

The Django admin interface provides management for all models:
- Players with inline summoner name management
- User management with role assignments
- Match and participation data
- Blog post moderation
- Newsletter subscriber management
- Official statistics monitoring

## Production Deployment

### Security Considerations
- HTTPS enforcement with HSTS
- Secure cookie configuration
- Comprehensive CSP implementation
- Rate limiting and throttling
- SQL injection protection through ORM

### Performance Optimization
- Database indexing for frequently queried fields
- Redis caching for expensive operations
- Pagination for large datasets
- Static file compression with WhiteNoise

## User Roles

- **USER**: Basic authenticated user
- **EDITOR**: Can create and manage blog posts
- **ADMIN**: Full system access including user and player management

## External API Integration

### PandaScore API
Used for fetching official tournament match data with team and player statistics.

### Riot Games API
Designed to integrate with Riot's API for summoner information and match history (implementation details in related services).

## Live Deployment

The API is currently deployed and accessible at:
- **Primary Domain**: https://api.fms-project.fun/
- **Backup Domain**: https://fms-django-1.onrender.com/

### API Base URLs
Use either of the above URLs as the base URL for API calls. For example:
- `GET https://api.fms-project.fun/api/players/` - List all players
- `POST https://api.fms-project.fun/api/login/` - User login

---

**Note**: This is a backend API. You'll need a separate frontend application to provide a user interface for this system.
