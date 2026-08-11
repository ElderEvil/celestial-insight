# Fix Authentication Flow Issues

## TL;DR

> **Quick Summary**: Core authentication flow is broken - even email+password login redirects fail. OAuth issues are symptoms of deeper authentication system problems.
> 
> **Deliverables**: 
> - Working email+password login with proper redirects
> - Fixed authentication middleware and session handling
> - Working OAuth flows (once core auth is fixed)
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: NO - sequential (authentication is foundational)
> **Critical Path**: Core auth → Sessions → Redirects → OAuth

---

## Context

### Original Request
User reports that even email+password login redirects don't work, indicating this is not OAuth-specific but a fundamental authentication flow issue.

### Current State Analysis
**Symptoms**:
- Email+password login redirects fail
- OAuth login flows fail  
- Telegram: "Bot domain invalid" 
- GitHub: OAuth flow doesn't complete

**Root Cause Hypothesis**:
- Core authentication flow is broken
- Login redirects not working for ANY method
- Session handling or middleware issues
- OAuth problems are secondary symptoms

### Authentication Flow Components
1. **Login Process**: Form submission → Authentication → Session creation
2. **Redirect Logic**: LOGIN_REDIRECT_URL → Dashboard/intended page  
3. **Session Management**: User state preservation across requests
4. **Middleware**: Authentication, session, CSRF middleware chain
5. **URL Configuration**: Login/logout URL routing

---

## Work Objectives

### Core Objective
Fix fundamental authentication flow to enable proper login, session management, and redirects for all authentication methods.

### Concrete Deliverables
- Email+password login works with proper redirects
- User sessions are created and maintained correctly
- LOGIN_REDIRECT_URL functions as intended
- Authentication middleware chain works properly
- OAuth flows work after core auth is fixed

### Definition of Done
- [ ] Can log in with email+password and redirect to dashboard
- [ ] User session persists across page navigation
- [ ] Logout works and redirects properly  
- [ ] OAuth flows complete successfully after core fix

### Must Have
- Working basic authentication flow
- Proper session management
- Correct redirect handling
- All authentication methods functional

### Must NOT Have (Guardrails)
- Broken session state
- Authentication bypasses or security holes
- Hardcoded redirect URLs
- Mixed authentication states

---

## Execution Strategy

### Sequential Execution Required

> Authentication is foundational - must fix core flow before OAuth.

```
Task 1: Diagnose Core Authentication System
├── Check Django authentication configuration
├── Verify session middleware and settings
├── Test basic login/logout flows
└── Analyze redirect logic and URLs

Task 2: Fix Authentication Middleware and Sessions
├── Verify middleware order and configuration  
├── Fix session settings if broken
├── Test session creation and persistence
└── Verify CSRF protection works

Task 3: Fix Login/Logout Redirects
├── Check LOGIN_REDIRECT_URL and LOGOUT_REDIRECT_URL
├── Test redirect logic after login
├── Fix any URL configuration issues
└── Verify dashboard access after login

Task 4: Test and Fix OAuth Integration
├── Test OAuth flows with working core auth
├── Fix remaining OAuth-specific issues
├── Verify all authentication methods work
└── Test user creation and account linking

Critical Path: All tasks sequential (authentication is foundational)
```

### Agent Dispatch Summary

| Task | Recommended Agent | Notes |
|------|------------------|-------|
| 1 | category="unspecified-high", skills=[] | Complex authentication diagnosis |
| 2 | category="quick", skills=[] | Configuration fixes |
| 3 | category="quick", skills=[] | URL and redirect fixes |
| 4 | category="visual-engineering", skills=["dev-browser"] | End-to-end testing |

---

## TODOs

- [ ] 1. Diagnose Core Authentication System

  **What to do**:
  - Test basic email+password login flow manually
  - Check Django authentication configuration and middleware
  - Verify session settings and session creation
  - Analyze login/logout URL configuration
  - Test redirect behavior after login/logout
  - Document specific authentication failures

  **Must NOT do**:
  - Don't modify configurations during diagnosis
  - Don't test OAuth until core auth is working

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Complex authentication system analysis requiring deep Django understanding
  - **Skills**: `[]`
    - Reason: Uses core Django tools and manual testing

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 1)
  - **Blocks**: Tasks 2, 3, 4 (all depend on core diagnosis)
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (authentication configuration):
  - `celestial_insight/settings.py:83-96` - MIDDLEWARE configuration
  - `celestial_insight/settings.py:117-122` - AUTHENTICATION_BACKENDS
  - `celestial_insight/settings.py:206-214` - Login/logout redirect URLs
  - `celestial_insight/urls.py:11-12` - allauth URL configuration

  **Django Core References** (authentication components):
  - Django sessions: SESSION_* settings and session middleware
  - Django auth: Authentication backends and login/logout views
  - CSRF: CSRF middleware and token handling
  - Sites framework: SITE_ID and redirect URL generation

  **Template References** (login UI):
  - `templates/account/login.html` - Login form and submission
  - Login form: Method, action, CSRF token inclusion
  - Social auth buttons: How OAuth is initiated from UI

  **WHY Each Reference Matters**:
  - Middleware order: Critical for authentication flow
  - Auth backends: Must be properly configured for login
  - Redirect URLs: Where users go after successful login
  - Login template: How authentication is initiated

  **Acceptance Criteria**:

  **Automated Verification**:
  ```bash
  # Agent checks authentication configuration
  uv run python -c "
  from django.conf import settings
  import django
  django.setup()
  
  print('=== Authentication Configuration ===')
  print('MIDDLEWARE:')
  for mw in settings.MIDDLEWARE:
      if 'auth' in mw.lower() or 'session' in mw.lower() or 'csrf' in mw.lower():
          print(f'  ✓ {mw}')
  
  print('\\nAUTHENTICATION_BACKENDS:')
  for backend in settings.AUTHENTICATION_BACKENDS:
      print(f'  ✓ {backend}')
      
  print('\\nRedirect URLs:')
  print(f'  LOGIN_URL: {getattr(settings, \"LOGIN_URL\", \"NOT SET\")}')
  print(f'  LOGIN_REDIRECT_URL: {getattr(settings, \"LOGIN_REDIRECT_URL\", \"NOT SET\")}')
  print(f'  LOGOUT_REDIRECT_URL: {getattr(settings, \"LOGOUT_REDIRECT_URL\", \"NOT SET\")}')
  
  print('\\nSession Configuration:')
  print(f'  SESSION_ENGINE: {getattr(settings, \"SESSION_ENGINE\", \"default\")}')
  print(f'  SESSION_COOKIE_AGE: {getattr(settings, \"SESSION_COOKIE_AGE\", \"default\")}')
  "
  
  # Agent tests basic authentication URLs
  uv run python manage.py shell -c "
  from django.urls import reverse, NoReverseMatch
  
  auth_urls = ['account_login', 'account_logout', 'account_signup']
  for url_name in auth_urls:
      try:
          url = reverse(url_name)
          print(f'{url_name}: {url}')
      except NoReverseMatch:
          print(f'{url_name}: NOT FOUND')
  "
  
  # Agent tests login page accessibility
  uv run python manage.py runserver --noreload &
  sleep 3
  
  echo "Testing login page accessibility:"
  login_status=$(curl -s -w "%{http_code}" -o /tmp/login_page.html http://127.0.0.1:8000/accounts/login/)
  echo "Login page status: $login_status"
  
  if [ "$login_status" = "200" ]; then
      echo "Checking login form:"
      grep -q 'method="post"' /tmp/login_page.html && echo "  ✓ POST method found" || echo "  ✗ POST method missing"
      grep -q 'csrfmiddlewaretoken' /tmp/login_page.html && echo "  ✓ CSRF token found" || echo "  ✗ CSRF token missing"
      grep -q 'email' /tmp/login_page.html && echo "  ✓ Email field found" || echo "  ✗ Email field missing"
      grep -q 'password' /tmp/login_page.html && echo "  ✓ Password field found" || echo "  ✗ Password field missing"
  fi
  
  pkill -f runserver
  rm -f /tmp/login_page.html
  ```

  **Manual Testing Protocol**:
  ```bash
  # Agent performs manual login test
  echo "=== Manual Login Test Protocol ==="
  echo "1. Start development server"
  echo "2. Navigate to /accounts/login/"
  echo "3. Fill in email/password form"  
  echo "4. Submit form"
  echo "5. Check if redirect occurs"
  echo "6. Verify target page loads"
  echo "7. Check if user is authenticated"
  echo "8. Test logout redirect"
  ```

  **Evidence to Capture**:
  - [ ] Authentication middleware configuration
  - [ ] Login/logout URL mappings
  - [ ] Login form analysis (POST method, CSRF, fields)
  - [ ] Manual login test results
  - [ ] Session configuration verification

  **Commit**: NO
  - This is diagnosis only, no code changes

- [ ] 2. Fix Authentication Middleware and Sessions

  **What to do**:
  - Based on diagnosis, fix authentication middleware order/configuration
  - Ensure session middleware is properly configured
  - Fix any session settings that prevent login state persistence
  - Verify CSRF middleware is working correctly
  - Test session creation after login

  **Must NOT do**:
  - Don't disable security middleware without good reason
  - Don't change authentication backends unnecessarily

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Configuration fixes based on diagnosis
  - **Skills**: `[]`
    - Reason: Django settings and middleware configuration

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 2)
  - **Blocks**: Tasks 3, 4
  - **Blocked By**: Task 1 (needs diagnosis results)

  **References**:

  **Pattern References** (middleware configuration):
  - `celestial_insight/settings.py:83-96` - MIDDLEWARE order (critical for auth)
  - Django docs: Recommended middleware order for authentication
  - Session middleware: Must be before authentication middleware

  **Session Configuration** (settings to verify):
  - SESSION_ENGINE: Database sessions vs other engines
  - SESSION_COOKIE_AGE: Session timeout configuration
  - SESSION_SAVE_EVERY_REQUEST: Session persistence behavior

  **Authentication References** (core components):
  - AuthenticationMiddleware: Must be after SessionMiddleware
  - CsrfViewMiddleware: CSRF protection for forms
  - allauth.account.middleware.AccountMiddleware: For allauth integration

  **WHY Each Reference Matters**:
  - Middleware order: Incorrect order breaks authentication flow
  - Session config: Required for login state persistence
  - CSRF: Protects login forms from attacks

  **Acceptance Criteria**:

  **Automated Verification**:
  ```bash
  # Agent verifies middleware fixes
  uv run python -c "
  from django.conf import settings
  
  middleware = settings.MIDDLEWARE
  session_idx = next((i for i, mw in enumerate(middleware) if 'SessionMiddleware' in mw), -1)
  auth_idx = next((i for i, mw in enumerate(middleware) if 'AuthenticationMiddleware' in mw), -1)
  csrf_idx = next((i for i, mw in enumerate(middleware) if 'CsrfViewMiddleware' in mw), -1)
  
  print('Middleware order verification:')
  print(f'SessionMiddleware position: {session_idx}')
  print(f'AuthenticationMiddleware position: {auth_idx}')
  print(f'CsrfViewMiddleware position: {csrf_idx}')
  
  if session_idx < auth_idx:
      print('✓ SessionMiddleware before AuthenticationMiddleware')
  else:
      print('✗ WRONG ORDER: SessionMiddleware must be before AuthenticationMiddleware')
      
  if csrf_idx > 0:
      print('✓ CsrfViewMiddleware present')
  else:
      print('✗ CsrfViewMiddleware missing')
  "
  
  # Agent tests session creation
  uv run python manage.py shell -c "
  from django.test import Client
  
  client = Client()
  response = client.get('/accounts/login/')
  
  print('Session test:')
  print(f'Response status: {response.status_code}')
  print(f'Session key exists: {bool(client.session.session_key)}')
  print(f'CSRF cookie set: {\"csrftoken\" in response.cookies}')
  "
  
  # Agent tests authentication with test client
  uv run python manage.py shell -c "
  from django.test import Client
  from django.contrib.auth.models import User
  
  # Create test user if needed
  user, created = User.objects.get_or_create(
      email='test@example.com',
      defaults={'username': 'testuser', 'is_active': True}
  )
  if created:
      user.set_password('testpass123')
      user.save()
  
  client = Client()
  login_success = client.login(username='test@example.com', password='testpass123')
  
  print('Authentication test:')
  print(f'User created: {created}')
  print(f'Login successful: {login_success}')
  print(f'User authenticated: {client.session.get(\"_auth_user_id\") == str(user.id)}')
  "
  ```

  **Evidence to Capture**:
  - [ ] Middleware order verification
  - [ ] Session creation confirmation
  - [ ] Authentication test results

  **Commit**: YES (if middleware fixes needed)
  - Message: `fix(auth): correct middleware order for authentication flow`
  - Files: `celestial_insight/settings.py`
  - Pre-commit: `uv run python -c "from django.conf import settings; print('Middleware OK')"`

- [ ] 3. Fix Login/Logout Redirects

  **What to do**:
  - Fix LOGIN_REDIRECT_URL to point to working dashboard
  - Verify dashboard view exists and is accessible
  - Test redirect behavior after successful login
  - Fix logout redirect if needed
  - Ensure redirect URLs are properly configured

  **Must NOT do**:
  - Don't hardcode redirect URLs
  - Don't create redirect loops

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: URL configuration and redirect testing
  - **Skills**: `[]`
    - Reason: Django URL and view configuration

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 3)
  - **Blocks**: Task 4 (OAuth testing)
  - **Blocked By**: Tasks 1, 2 (needs working core auth)

  **References**:

  **Pattern References** (redirect configuration):
  - `celestial_insight/settings.py:206-214` - Current redirect URL settings
  - `celestial_insight/urls.py:16` - Dashboard URL pattern
  - `tarot.views.dashboard` - Dashboard view implementation

  **Django Redirect References** (redirect mechanism):
  - LOGIN_REDIRECT_URL: Where users go after login
  - LOGOUT_REDIRECT_URL: Where users go after logout  
  - Dashboard view: Must be accessible to authenticated users

  **URL Pattern References** (routing):
  - Dashboard route: `/dashboard/` pattern and view
  - Login route: `/accounts/login/` from allauth
  - URL reversal: How Django generates redirect URLs

  **WHY Each Reference Matters**:
  - Redirect URLs: Must point to working, accessible pages
  - Dashboard view: Must handle authenticated user properly
  - URL patterns: Must be correctly configured for routing

  **Acceptance Criteria**:

  **Automated Verification**:
  ```bash
  # Agent verifies redirect URL configuration
  uv run python -c "
  from django.conf import settings
  from django.urls import reverse, NoReverseMatch
  
  print('Redirect URL configuration:')
  login_redirect = getattr(settings, 'LOGIN_REDIRECT_URL', None)
  logout_redirect = getattr(settings, 'LOGOUT_REDIRECT_URL', None)
  
  print(f'LOGIN_REDIRECT_URL: {login_redirect}')
  print(f'LOGOUT_REDIRECT_URL: {logout_redirect}')
  
  # Test if redirect URLs are valid
  try:
      if login_redirect:
          print(f'Login redirect accessible: {login_redirect}')
  except Exception as e:
      print(f'Login redirect error: {e}')
      
  # Test dashboard URL
  try:
      dashboard_url = reverse('dashboard')
      print(f'Dashboard URL: {dashboard_url}')
      print(f'Dashboard matches redirect: {dashboard_url == login_redirect}')
  except NoReverseMatch:
      print('Dashboard URL not found')
  "
  
  # Agent tests dashboard accessibility
  uv run python manage.py shell -c "
  from django.test import Client
  from django.contrib.auth.models import User
  
  # Get or create test user
  user = User.objects.filter(email='test@example.com').first()
  if not user:
      user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
  
  client = Client()
  client.force_login(user)
  
  response = client.get('/dashboard/')
  print(f'Dashboard accessibility:')
  print(f'  Status: {response.status_code}')
  print(f'  Accessible: {response.status_code == 200}')
  print(f'  User authenticated in response: {hasattr(response, \"context\") and response.context and response.context.get(\"user\") == user}')
  "
  
  # Agent tests complete login flow
  uv run python manage.py runserver --noreload &
  sleep 3
  
  echo "Testing login redirect flow:"
  
  # Get login page and extract CSRF token
  login_page=$(curl -s -c /tmp/cookies.txt http://127.0.0.1:8000/accounts/login/)
  csrf_token=$(echo "$login_page" | grep -o 'name="csrfmiddlewaretoken" value="[^"]*"' | cut -d'"' -f4)
  
  if [ -n "$csrf_token" ]; then
      echo "CSRF token extracted: ${csrf_token:0:20}..."
      
      # Attempt login (will fail but shows redirect behavior)
      login_response=$(curl -s -w "%{http_code}:%{redirect_url}" -b /tmp/cookies.txt -c /tmp/cookies.txt \
          -d "csrfmiddlewaretoken=$csrf_token&login=test@example.com&password=testpass123" \
          -X POST http://127.0.0.1:8000/accounts/login/)
          
      echo "Login response: $login_response"
  else
      echo "Could not extract CSRF token"
  fi
  
  pkill -f runserver
  rm -f /tmp/cookies.txt
  ```

  **Evidence to Capture**:
  - [ ] Redirect URL configuration verification
  - [ ] Dashboard accessibility confirmation  
  - [ ] Login flow redirect testing

  **Commit**: YES (if redirect fixes needed)
  - Message: `fix(auth): configure proper login/logout redirects`
  - Files: `celestial_insight/settings.py`
  - Pre-commit: `uv run python -c "from django.urls import reverse; print('Dashboard:', reverse('dashboard'))"`

- [ ] 4. Test and Fix OAuth Integration

  **What to do**:
  - With working core authentication, test OAuth flows
  - Fix any remaining OAuth-specific issues  
  - Test user creation and social account linking
  - Verify all authentication methods work together
  - Test complete user journey from OAuth to dashboard

  **Must NOT do**:
  - Don't modify core authentication settings
  - Don't commit temporary test accounts

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Requires browser automation for complete OAuth testing
  - **Skills**: `["dev-browser"]`
    - Reason: OAuth flows require external provider interaction

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 4 - Final)
  - **Blocks**: None (final verification task)
  - **Blocked By**: Tasks 1, 2, 3 (needs working core authentication)

  **References**:

  **Pattern References** (OAuth integration):
  - `celestial_insight/settings.py:181-201` - OAuth provider configurations
  - `users/adapters.py` - Custom account adapter for user merging
  - `templates/account/login.html` - Social login buttons

  **Authentication Flow References** (complete user journey):
  - OAuth initiation → Provider → Callback → User creation → Login → Dashboard
  - Account linking: How OAuth accounts connect to Django users
  - Session persistence: User stays logged in after OAuth

  **Testing References** (OAuth flow verification):
  - GitHub OAuth: Complete flow from button to dashboard
  - Telegram OAuth: Domain validation and user creation
  - Account adapter: Custom logic for merging accounts

  **WHY Each Reference Matters**:
  - OAuth config: Must work with fixed core authentication
  - Account adapter: Critical for user account management
  - Complete flow: Proves entire authentication system works

  **Acceptance Criteria**:

  **Automated Verification (Browser Testing)**:
  ```bash
  # Agent starts development server for OAuth testing
  uv run python manage.py runserver --noreload &
  SERVER_PID=$!
  sleep 5
  
  # Browser automation test (via dev-browser skill):
  # 1. Navigate to login page (http://127.0.0.1:8000/accounts/login/)
  # 2. Verify social login buttons are present and functional
  # 3. Test email+password login works with redirect
  # 4. Test GitHub OAuth initiation (redirect to github.com)
  # 5. Test Telegram OAuth initiation (redirect to telegram without domain error)
  # 6. Verify login redirects to dashboard correctly
  # 7. Test logout and redirect functionality
  # 8. Screenshot evidence of working authentication flows
  
  # Cleanup
  kill $SERVER_PID
  ```

  **For Authentication System Verification**:
  ```bash
  # Agent verifies complete authentication system
  uv run python manage.py shell -c "
  from django.contrib.auth.models import User
  from django.test import Client
  from django.urls import reverse
  
  print('=== Complete Authentication Test ===')
  
  # Test user creation
  user, created = User.objects.get_or_create(
      email='auth-test@example.com',
      defaults={'username': 'authtest', 'is_active': True}
  )
  if created:
      user.set_password('authtest123')
      user.save()
      
  client = Client()
  
  # Test login
  login_success = client.login(username='auth-test@example.com', password='authtest123')
  print(f'✓ Login successful: {login_success}')
  
  # Test dashboard access
  dashboard_response = client.get(reverse('dashboard'))
  print(f'✓ Dashboard accessible: {dashboard_response.status_code == 200}')
  
  # Test logout
  client.logout()
  dashboard_after_logout = client.get(reverse('dashboard'))
  print(f'✓ Dashboard protected after logout: {dashboard_after_logout.status_code != 200}')
  
  # Test OAuth URLs
  oauth_providers = ['github', 'google', 'telegram']
  for provider in oauth_providers:
      try:
          login_url = reverse(f'{provider}_login')
          response = client.get(login_url)
          print(f'✓ {provider} OAuth: {response.status_code} (should redirect)')
      except Exception as e:
          print(f'✗ {provider} OAuth error: {e}')
  
  # Cleanup test user
  if created:
      user.delete()
  "
  ```

  **Evidence to Capture**:
  - [ ] Screenshot of working login page (.sisyphus/evidence/login-working.png)
  - [ ] Screenshot of successful dashboard access (.sisyphus/evidence/dashboard-access.png)
  - [ ] Screenshot of working OAuth buttons (.sisyphus/evidence/oauth-buttons-working.png)
  - [ ] Terminal output showing complete authentication test results
  - [ ] Confirmation that all authentication methods work

  **Commit**: YES (if OAuth fixes needed)
  - Message: `fix(auth): complete oauth integration with working core auth`
  - Files: OAuth-related files if updated
  - Pre-commit: `uv run python manage.py check --deploy`

---

## Success Criteria

### Verification Commands
```bash
# Test core authentication
uv run python manage.py shell -c "from django.test import Client; c = Client(); from django.contrib.auth.models import User; u = User.objects.create_user('test', 'test@test.com', 'test123'); print('Login:', c.login(username='test@test.com', password='test123')); u.delete()"  # Expected: Login: True

# Test dashboard redirect
curl -s -w "%{http_code}" -o /dev/null http://127.0.0.1:8000/dashboard/  # Expected: 302 (redirect to login) or 200 (if logged in)

# Test OAuth initiation
curl -s -w "GitHub: %{http_code}\n" -o /dev/null http://127.0.0.1:8000/accounts/github/login/  # Expected: 302
curl -s -w "Telegram: %{http_code}\n" -o /dev/null http://127.0.0.1:8000/accounts/telegram/login/  # Expected: 302

# Test login page
curl -s -w "%{http_code}" -o /dev/null http://127.0.0.1:8000/accounts/login/  # Expected: 200
```

### Final Checklist
- [ ] Email+password login works with proper redirects
- [ ] User sessions persist across requests
- [ ] Dashboard is accessible after login
- [ ] Logout redirects properly
- [ ] GitHub OAuth flow completes successfully
- [ ] Telegram OAuth works without "Bot domain invalid" error
- [ ] All authentication methods redirect to dashboard