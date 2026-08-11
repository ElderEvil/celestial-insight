# Fix Social Authentication Configuration

## TL;DR

> **Quick Summary**: Fix critical django-allauth configuration issues causing Google OAuth to fail after successful callback. GitHub works because it's more forgiving of missing sites framework.
> 
> **Deliverables**: 
> - Working Google OAuth sign-in
> - Secure OAuth credential management  
> - Proper django-allauth configuration per best practices
> - All social providers properly configured
> 
> **Estimated Effort**: Short
> **Parallel Execution**: NO - sequential (config dependencies)
> **Critical Path**: Site framework → OAuth config → security cleanup

---

## Context

### Original Request
User wants to analyze if social sign-in is set up correctly. GitHub works but Google OAuth fails with "returns but fails" behavior.

### Research Findings
**Current OAuth Flow**:
- Google OAuth callback succeeds (HTTP 302 redirect)
- Django/allauth fails after callback due to missing sites framework
- Missing `SITE_ID` and `django.contrib.sites` configuration

**From django-allauth docs (v65.14.0)**:
- Sites framework is **required** for proper OAuth redirect handling
- Google OAuth is stricter about redirect_uri validation than GitHub
- Security best practices require HTTPS, PKCE, and secure credential storage

### Root Cause
Google OAuth callback processes successfully but django-allauth cannot complete user creation/login due to missing Site configuration. GitHub is more forgiving of this misconfiguration.

---

## Work Objectives

### Core Objective
Fix django-allauth configuration to enable working Google OAuth while maintaining GitHub functionality and implementing security best practices.

### Concrete Deliverables
- Google OAuth sign-in works end-to-end
- All OAuth credentials secured (not in git)
- Django sites framework properly configured
- All social providers correctly installed and configured

### Definition of Done
- [ ] Can sign in with Google account successfully
- [ ] Can sign in with GitHub account (regression test)
- [ ] No OAuth credentials in git repository
- [ ] All django-allauth configuration follows official best practices

### Must Have
- Working Google OAuth flow
- Secure credential management
- Proper sites framework configuration

### Must NOT Have (Guardrails)
- OAuth secrets committed to git
- Mixed configuration methods (settings.py + admin)
- Deprecated django-allauth settings

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES
- **User wants tests**: Manual-only (OAuth requires external services)
- **Framework**: pytest (existing)

### Automated Verification Only

Each TODO includes EXECUTABLE verification procedures that agents can run directly:

**For OAuth Configuration** (using Bash commands):
```bash
# Agent verifies settings are correct
python -c "from django.conf import settings; print('SITE_ID:', getattr(settings, 'SITE_ID', 'MISSING'))"
python -c "from django.conf import settings; print('Sites in INSTALLED_APPS:', 'django.contrib.sites' in settings.INSTALLED_APPS)"
```

**For OAuth Endpoints** (using curl via Bash):
```bash
# Agent tests OAuth initiation endpoints
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/accounts/google/login/
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/accounts/github/login/
# Assert: Both return 302 (redirect to OAuth provider)
```

**For Django Admin Site Configuration** (using Django shell):
```bash
# Agent verifies Site object exists
python manage.py shell -c "
from django.contrib.sites.models import Site
site = Site.objects.get(id=1)
print(f'Site domain: {site.domain}')
print(f'Site name: {site.name}')
"
```

**Evidence Requirements**:
- Settings verification output captured
- HTTP response codes from OAuth endpoints
- Site model configuration confirmed
- Browser test screenshots (manual backup verification)

---

## Execution Strategy

### Sequential Execution Required

> OAuth configuration has strict dependencies. Must be done sequentially.

```
Task 1: Fix sites framework configuration
├── Add django.contrib.sites to INSTALLED_APPS  
├── Add SITE_ID = 1 to settings
└── Run migrations

Task 2: Fix social provider configuration  
├── Add missing Telegram provider to INSTALLED_APPS
├── Verify OAuth callback URLs in settings
└── Configure Site domain in Django admin

Task 3: Security cleanup
├── Move OAuth credentials to secure storage
├── Add .env to .gitignore
└── Rotate exposed credentials

Task 4: Verification testing
└── Test Google and GitHub OAuth flows

Critical Path: All tasks sequential (each depends on previous)
```

### Agent Dispatch Summary

| Task | Recommended Agent | Notes |
|------|------------------|-------|
| 1 | category="quick", skills=[] | Simple settings changes |
| 2 | category="quick", skills=[] | Provider configuration |  
| 3 | category="quick", skills=[] | Security cleanup |
| 4 | category="visual-engineering", skills=["dev-browser"] | OAuth flow testing |

---

## TODOs

- [ ] 1. Fix Django Sites Framework Configuration

  **What to do**:
  - Add `django.contrib.sites` to INSTALLED_APPS in settings.py
  - Add `SITE_ID = 1` to settings.py
  - Run Django migrations to create sites tables
  - Verify sites framework is working

  **Must NOT do**:
  - Don't modify any OAuth provider configurations yet
  - Don't change existing allauth settings

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple settings.py changes and migration command
  - **Skills**: `[]`
    - Reason: Standard Django configuration, no specialized skills needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 1)
  - **Blocks**: Tasks 2, 3, 4 (all depend on sites framework)
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (existing code to follow):
  - `celestial_insight/settings.py:68-73` - INSTALLED_APPS structure to follow
  - `celestial_insight/settings.py:168-203` - Allauth settings section to add SITE_ID

  **API/Type References** (contracts to implement against):
  - Django Sites Framework: `django.contrib.sites` - Required for allauth OAuth redirects
  - Settings pattern: `SITE_ID = 1` - Default site ID for single-site setup

  **Documentation References**:
  - Official docs: `https://docs.djangoproject.com/en/5.0/ref/contrib/sites/` - Django sites framework setup
  - Allauth docs: `https://docs.allauth.org/en/latest/installation/quickstart.html` - Sites requirement

  **WHY Each Reference Matters**:
  - `settings.py` structure: Follow existing INSTALLED_APPS formatting and placement
  - Sites framework: Required by django-allauth for proper OAuth redirect handling
  - `SITE_ID = 1`: Default site for single-site Django installations

  **Acceptance Criteria**:

  **Automated Verification**:
  ```bash
  # Agent verifies sites framework is configured
  python -c "
  from django.conf import settings
  print('SITE_ID:', getattr(settings, 'SITE_ID', 'MISSING'))
  print('Sites in INSTALLED_APPS:', 'django.contrib.sites' in settings.INSTALLED_APPS)
  "
  # Assert: SITE_ID prints "1" and Sites prints "True"
  
  # Agent verifies migrations completed
  python manage.py showmigrations sites
  # Assert: All sites migrations show [X] (applied)
  
  # Agent verifies Site model works
  python manage.py shell -c "
  from django.contrib.sites.models import Site
  site, created = Site.objects.get_or_create(id=1, defaults={'domain': '127.0.0.1:8000', 'name': 'Celestial Insight Dev'})
  print(f'Site created: {created}, Domain: {site.domain}')
  "
  # Assert: Output shows Site domain
  ```

  **Evidence to Capture**:
  - [ ] Settings verification output (SITE_ID and sites in INSTALLED_APPS)
  - [ ] Migration status output
  - [ ] Site model creation confirmation

  **Commit**: YES
  - Message: `fix(auth): add django.contrib.sites framework for allauth OAuth`
  - Files: `celestial_insight/settings.py`
  - Pre-commit: `python -c "from django.conf import settings; print(settings.SITE_ID)"`

- [ ] 2. Fix Social Provider Configuration

  **What to do**:
  - Add `allauth.socialaccount.providers.telegram` to INSTALLED_APPS
  - Configure Site domain in Django admin to match OAuth callback URLs  
  - Verify all provider URL patterns are correctly configured
  - Update Site object with correct domain for OAuth redirects

  **Must NOT do**:
  - Don't change OAuth credentials yet (security task)
  - Don't modify existing GitHub/Google provider settings

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Configuration changes and Django admin setup
  - **Skills**: `[]`
    - Reason: Standard Django configuration and admin tasks

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 2) 
  - **Blocks**: Tasks 3, 4
  - **Blocked By**: Task 1 (needs sites framework working)

  **References**:

  **Pattern References** (existing code to follow):
  - `celestial_insight/settings.py:68-73` - INSTALLED_APPS pattern for adding Telegram provider
  - `celestial_insight/settings.py:173-195` - SOCIALACCOUNT_PROVIDERS config showing Telegram is configured
  - `celestial_insight/urls.py:11-14` - URL pattern structure for provider URLs

  **API/Type References** (contracts to implement against):
  - Telegram provider: `allauth.socialaccount.providers.telegram` - Required in INSTALLED_APPS
  - Site model: `django.contrib.sites.models.Site` - Domain must match OAuth callback URLs

  **Documentation References**:
  - Allauth providers: `https://docs.allauth.org/en/latest/socialaccount/providers/` - Provider installation requirements
  - OAuth callback URLs: `http://127.0.0.1:8000/accounts/google/login/callback/` - Must match Site domain

  **WHY Each Reference Matters**:
  - Telegram provider: Currently configured in SOCIALACCOUNT_PROVIDERS but missing from INSTALLED_APPS
  - Site domain: OAuth providers validate callback URLs against Site domain
  - URL patterns: Ensure all provider callback URLs are properly routed

  **Acceptance Criteria**:

  **Automated Verification**:
  ```bash
  # Agent verifies Telegram provider is installed
  python -c "
  from django.conf import settings
  providers = [app for app in settings.INSTALLED_APPS if 'telegram' in app]
  print(f'Telegram provider installed: {len(providers) > 0}')
  print(f'Found: {providers}')
  "
  # Assert: Output shows telegram provider found
  
  # Agent verifies Site domain is configured correctly
  python manage.py shell -c "
  from django.contrib.sites.models import Site
  site = Site.objects.get(id=1)
  print(f'Site domain: {site.domain}')
  print(f'Callback URL would be: http://{site.domain}/accounts/google/login/callback/')
  "
  # Assert: Domain matches development server (127.0.0.1:8000)
  
  # Agent verifies OAuth URLs are accessible
  python manage.py runserver --noreload &
  sleep 3
  curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/accounts/google/login/
  curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/accounts/github/login/
  pkill -f runserver
  # Assert: Both return 302 (redirect to OAuth provider)
  ```

  **Evidence to Capture**:
  - [ ] Provider installation verification output
  - [ ] Site domain configuration output  
  - [ ] OAuth endpoint HTTP response codes

  **Commit**: YES
  - Message: `fix(auth): add telegram provider to INSTALLED_APPS and configure site domain`
  - Files: `celestial_insight/settings.py`
  - Pre-commit: `python -c "from django.apps import apps; print(apps.is_installed('allauth.socialaccount.providers.telegram'))"`

- [ ] 3. Security Cleanup - Secure OAuth Credentials

  **What to do**:
  - Add `.env` to `.gitignore` if not already present
  - Create `.env.example` template without actual secrets
  - Document that OAuth credentials need to be rotated due to exposure
  - Verify environment variable loading is working correctly
  - Add security settings recommended by django-allauth

  **Must NOT do**:
  - Don't include actual OAuth secrets in any committed files
  - Don't remove existing OAuth functionality during cleanup

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: File operations and configuration updates
  - **Skills**: `[]`
    - Reason: Standard security best practices and file management

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 3)
  - **Blocks**: Task 4 (verification testing)
  - **Blocked By**: Task 2 (needs working OAuth config)

  **References**:

  **Pattern References** (existing code to follow):
  - `.env.example:1-20` - Template pattern for environment variables without secrets
  - `celestial_insight/settings.py:173-195` - Environment variable usage pattern with os.getenv()
  - `.gitignore` - File exclusion patterns (if exists)

  **Security References** (django-allauth best practices):
  - Allauth security: `https://docs.allauth.org/en/latest/common/security.html` - OAuth security settings
  - Django security: `https://docs.djangoproject.com/en/5.0/topics/security/` - General Django security

  **Documentation References**:
  - Environment variables: OAuth credentials should never be in version control
  - Credential rotation: Exposed credentials in git history require immediate rotation

  **WHY Each Reference Matters**:
  - `.env` exclusion: Prevents future credential leaks in version control
  - Environment pattern: Shows how to properly reference OAuth secrets
  - Security settings: Implement recommended django-allauth security configuration

  **Acceptance Criteria**:

  **Automated Verification**:
  ```bash
  # Agent verifies .env is in .gitignore
  if [ -f .gitignore ]; then
    grep -q "^\.env$" .gitignore && echo ".env in gitignore: YES" || echo ".env in gitignore: NO"
  else
    echo ".gitignore file: NOT FOUND"
  fi
  # Assert: .env is properly excluded from git
  
  # Agent verifies environment variables are loaded
  python -c "
  import os
  github_id = os.getenv('GITHUB_CLIENT_ID', 'NOT_FOUND')
  google_id = os.getenv('GOOGLE_CLIENT_ID', 'NOT_FOUND') 
  print(f'GitHub client ID loaded: {github_id != \"NOT_FOUND\"}')
  print(f'Google client ID loaded: {google_id != \"NOT_FOUND\"}')
  "
  # Assert: Both environment variables are loaded
  
  # Agent verifies security settings are applied
  python -c "
  from django.conf import settings
  login_on_get = getattr(settings, 'SOCIALACCOUNT_LOGIN_ON_GET', None)
  print(f'SOCIALACCOUNT_LOGIN_ON_GET: {login_on_get}')
  "
  # Assert: Security setting is properly configured
  ```

  **Evidence to Capture**:
  - [ ] .gitignore verification output
  - [ ] Environment variable loading confirmation
  - [ ] Security settings verification

  **Commit**: YES
  - Message: `security(auth): secure OAuth credentials and apply security best practices`
  - Files: `.gitignore, .env.example`
  - Pre-commit: `grep -q "^\.env$" .gitignore && echo "OK"`

- [ ] 4. Verification Testing - Test OAuth Flows

  **What to do**:
  - Test Google OAuth sign-in flow end-to-end
  - Test GitHub OAuth sign-in flow (regression test)
  - Verify OAuth callback URLs work correctly
  - Test user creation and login with both providers
  - Verify Telegram OAuth is properly configured (if credentials available)

  **Must NOT do**:
  - Don't modify any configuration during testing
  - Don't commit test data or temporary files

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Requires browser automation to test OAuth flows
  - **Skills**: `["dev-browser"]`
    - Reason: OAuth testing requires navigating to external providers and back

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 4 - Final)
  - **Blocks**: None (final task)
  - **Blocked By**: Tasks 1, 2, 3 (needs complete configuration)

  **References**:

  **Pattern References** (existing code to follow):
  - `templates/account/login.html:20-35` - Login page with social auth buttons
  - `users/adapters.py:pre_social_login()` - Custom account merging logic  
  - `celestial_insight/settings.py:173-195` - OAuth provider configuration

  **API/Type References** (contracts to verify):
  - OAuth callback URLs: `/accounts/google/login/callback/`, `/accounts/github/login/callback/`
  - Login endpoints: `/accounts/google/login/`, `/accounts/github/login/`
  - User model: Verify social accounts are properly linked to Django users

  **Test References** (verification patterns):
  - OAuth flow: Initiate → Redirect to provider → Callback → User creation/login
  - Browser automation: Navigate, click, verify redirects and final authentication state

  **WHY Each Reference Matters**:
  - Login template: Shows how social auth buttons are rendered and work
  - Custom adapter: Critical for user account merging logic
  - OAuth endpoints: Must be accessible and properly configured

  **Acceptance Criteria**:

  **Automated Verification (Browser Testing)**:
  ```bash
  # Agent tests OAuth flows using dev-browser skill
  # Start development server
  python manage.py runserver &
  SERVER_PID=$!
  sleep 5
  
  # Browser automation test (via dev-browser skill):
  # 1. Navigate to login page
  # 2. Verify Google and GitHub sign-in buttons are present
  # 3. Click Google sign-in button  
  # 4. Verify redirect to Google OAuth (google.com domain)
  # 5. Click GitHub sign-in button
  # 6. Verify redirect to GitHub OAuth (github.com domain)
  # 7. Screenshot evidence of working OAuth initiation
  
  # Cleanup
  kill $SERVER_PID
  ```

  **For OAuth Configuration Verification** (using Django commands):
  ```bash
  # Agent verifies OAuth provider configuration
  python manage.py shell -c "
  from allauth.socialaccount.models import SocialApp
  from django.contrib.sites.models import Site
  
  site = Site.objects.get(id=1)
  print(f'Site domain: {site.domain}')
  
  # Check if providers are configured via settings
  from django.conf import settings
  providers = settings.SOCIALACCOUNT_PROVIDERS
  print(f'Configured providers: {list(providers.keys())}')
  
  # Verify OAuth URLs resolve
  from django.urls import reverse
  try:
    google_url = reverse('google_login')
    github_url = reverse('github_login')
    print(f'Google login URL: {google_url}')
    print(f'GitHub login URL: {github_url}')
  except Exception as e:
    print(f'URL resolution error: {e}')
  "
  # Assert: Providers are configured and URLs resolve properly
  ```

  **Evidence to Capture**:
  - [ ] Screenshot of login page with working OAuth buttons (.sisyphus/evidence/oauth-login-page.png)
  - [ ] Screenshot of Google OAuth redirect (.sisyphus/evidence/google-oauth-redirect.png)
  - [ ] Screenshot of GitHub OAuth redirect (.sisyphus/evidence/github-oauth-redirect.png)
  - [ ] Terminal output from OAuth configuration verification
  - [ ] Browser navigation logs showing successful redirects

  **Commit**: NO
  - This is verification only, no code changes

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `fix(auth): add django.contrib.sites framework for allauth OAuth` | `celestial_insight/settings.py` | `python -c "from django.conf import settings; print(settings.SITE_ID)"` |
| 2 | `fix(auth): add telegram provider and configure site domain` | `celestial_insight/settings.py` | `python -c "from django.apps import apps; print(apps.is_installed('allauth.socialaccount.providers.telegram'))"` |
| 3 | `security(auth): secure OAuth credentials and apply security best practices` | `.gitignore, .env.example` | `grep -q "^\.env$" .gitignore && echo "OK"` |

---

## Success Criteria

### Verification Commands
```bash
# Test Google OAuth initiation
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/accounts/google/login/  # Expected: 302

# Test GitHub OAuth initiation  
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/accounts/github/login/  # Expected: 302

# Verify Sites framework
python -c "from django.contrib.sites.models import Site; print(Site.objects.get(id=1).domain)"  # Expected: 127.0.0.1:8000

# Verify OAuth providers are installed
python -c "from django.apps import apps; print([app for app in apps.get_app_configs() if 'telegram' in app.name])"  # Expected: telegram provider listed
```

### Final Checklist
- [ ] Google OAuth sign-in works end-to-end
- [ ] GitHub OAuth sign-in still works (no regression)
- [ ] All OAuth credentials secured (not in git)
- [ ] Django sites framework properly configured
- [ ] All social providers correctly installed