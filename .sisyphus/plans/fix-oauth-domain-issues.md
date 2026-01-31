# Fix OAuth Domain Issues

## TL;DR

> **Quick Summary**: Diagnose and fix OAuth domain configuration issues for Telegram ("Bot domain invalid") and GitHub (OAuth flow failure).
> 
> **Deliverables**: 
> - Working Telegram OAuth with correct domain configuration
> - Working GitHub OAuth end-to-end flow
> - Proper OAuth app configurations in provider consoles
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: NO - sequential (diagnostic dependencies)
> **Critical Path**: Diagnose → Fix configs → Test flows

---

## Context

### Original Request
User reports two specific OAuth issues:
1. **Telegram**: "Bot domain invalid" error
2. **GitHub**: OAuth doesn't work (used to work before)

### Current State Analysis
**What's Working**:
- All OAuth endpoints return 302 redirects to correct provider URLs
- Settings configuration loads properly
- Site framework is configured (127.0.0.1:8000)

**What's Failing**:
- Telegram: Domain validation error from Telegram OAuth service
- GitHub: OAuth flow fails after redirect (callback processing issue)

### Root Cause Hypotheses
**Telegram Domain Issue**:
- Bot not configured for correct domain in @BotFather
- Redirect URI mismatch between app and Telegram bot settings
- Development domain (127.0.0.1:8000) not whitelisted

**GitHub Flow Issue**:
- GitHub OAuth app redirect URI mismatch
- Invalid/expired GitHub client credentials  
- Callback URL processing failure
- State parameter mismatch

---

## Work Objectives

### Core Objective
Diagnose and fix OAuth domain configuration issues to enable working Telegram and GitHub authentication flows.

### Concrete Deliverables
- Telegram OAuth completes without "Bot domain invalid" error
- GitHub OAuth flow works end-to-end (redirect → callback → user login)
- OAuth app configurations match actual callback URLs
- Proper domain whitelisting in provider consoles

### Definition of Done
- [ ] Can complete Telegram OAuth flow successfully
- [ ] Can complete GitHub OAuth flow successfully
- [ ] No domain validation errors from OAuth providers
- [ ] Callback URLs match provider app configurations

### Must Have
- Working OAuth flows for both providers
- Correct domain configuration in provider consoles
- Proper callback URL handling

### Must NOT Have (Guardrails)
- Mixed development/production URLs
- Insecure OAuth configurations
- Hardcoded domains in settings

---

## Execution Strategy

### Sequential Execution Required

> OAuth domain issues require systematic diagnosis and testing.

```
Task 1: Diagnose Current OAuth Configurations
├── Check Telegram bot settings via @BotFather commands
├── Verify GitHub OAuth app settings in GitHub developer console  
├── Analyze actual vs expected callback URLs
└── Document configuration mismatches

Task 2: Fix Telegram Domain Configuration  
├── Update Telegram bot domain whitelist if needed
├── Verify bot token and domain settings match
├── Test Telegram OAuth flow
└── Verify "Bot domain invalid" error is resolved

Task 3: Fix GitHub OAuth Configuration
├── Verify GitHub OAuth app redirect URI settings
├── Check GitHub client credentials validity
├── Test GitHub OAuth callback handling
└── Verify complete GitHub OAuth flow

Task 4: Comprehensive OAuth Testing
├── Test all OAuth flows end-to-end
├── Verify user creation and login works
├── Test OAuth error handling
└── Document working configurations

Critical Path: All tasks sequential (each builds on previous diagnosis)
```

### Agent Dispatch Summary

| Task | Recommended Agent | Notes |
|------|------------------|-------|
| 1 | category="unspecified-high", skills=[] | Diagnosis and analysis |
| 2 | category="quick", skills=[] | Configuration fixes |
| 3 | category="quick", skills=[] | Configuration fixes |
| 4 | category="visual-engineering", skills=["dev-browser"] | End-to-end testing |

---

## TODOs

- [ ] 1. Diagnose OAuth Configuration Issues

  **What to do**:
  - Extract and analyze current OAuth configurations
  - Check Telegram bot settings and domain whitelist requirements
  - Verify GitHub OAuth app configuration in developer console
  - Compare actual callback URLs vs configured URLs
  - Document specific configuration mismatches

  **Must NOT do**:
  - Don't modify configurations yet (diagnosis first)
  - Don't commit any temporary diagnostic code

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
    - Reason: Complex analysis requiring understanding of OAuth provider requirements
  - **Skills**: `[]`
    - Reason: Diagnostic work using existing tools and documentation

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 1)
  - **Blocks**: Tasks 2, 3, 4 (all depend on diagnosis)
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (existing code to analyze):
  - `celestial_insight/settings.py:181-201` - Current OAuth provider configurations
  - `celestial_insight/urls.py:11-15` - OAuth callback URL patterns
  - `.env` - OAuth credentials and bot tokens

  **Documentation References**:
  - Telegram OAuth: `https://core.telegram.org/widgets/login` - Domain requirements
  - GitHub OAuth: `https://docs.github.com/en/developers/apps/oauth-apps` - App configuration
  - Django sites: Site domain must match OAuth callback domains

  **External References** (provider console checks):
  - Telegram @BotFather: Check bot domain settings and commands
  - GitHub Developer Console: Verify OAuth app redirect URIs
  - OAuth callback URLs: Must be exact matches including trailing slashes

  **WHY Each Reference Matters**:
  - Current config: Shows what's configured vs what providers expect
  - Provider docs: Define exact domain validation requirements
  - Console settings: Where actual OAuth app configurations are stored

  **Acceptance Criteria**:

  **Automated Verification**:
  ```bash
  # Agent extracts current configurations
  uv run python -c "
  from django.conf import settings
  from django.contrib.sites.models import Site
  import json
  
  site = Site.objects.get(id=1)
  print(f'Site domain: {site.domain}')
  
  providers = settings.SOCIALACCOUNT_PROVIDERS
  for name, config in providers.items():
      print(f'\\n{name.upper()} Configuration:')
      print(f'  Client ID: {config[\"APP\"][\"client_id\"][:20]}...')
      print(f'  Callback URL: http://{site.domain}/accounts/{name}/login/callback/')
  "
  
  # Agent checks URL resolution
  uv run python manage.py shell -c "
  from django.urls import reverse
  providers = ['github', 'google', 'telegram']
  for provider in providers:
      try:
          callback_url = reverse(f'{provider}_callback')
          print(f'{provider}_callback: {callback_url}')
      except Exception as e:
          print(f'{provider}_callback: ERROR - {e}')
  "
  
  # Agent tests OAuth initiation
  uv run python manage.py runserver --noreload &
  sleep 3
  echo "Current OAuth redirect URLs:"
  curl -s -w "GitHub: %{redirect_url}\\n" -o /dev/null http://127.0.0.1:8000/accounts/github/login/
  curl -s -w "Telegram: %{redirect_url}\\n" -o /dev/null http://127.0.0.1:8000/accounts/telegram/login/
  pkill -f runserver
  ```

  **Evidence to Capture**:
  - [ ] Current OAuth provider configurations (client IDs, callback URLs)
  - [ ] Actual redirect URLs generated by OAuth providers
  - [ ] Analysis of configuration mismatches
  - [ ] Provider-specific requirements documentation

  **Commit**: NO
  - This is analysis only, no code changes

- [ ] 2. Fix Telegram Domain Configuration

  **What to do**:
  - Based on diagnosis, fix Telegram bot domain configuration
  - Update bot settings via @BotFather if needed
  - Ensure callback URL matches bot domain whitelist
  - Verify bot token corresponds to correct bot
  - Test Telegram OAuth flow to confirm "Bot domain invalid" is resolved

  **Must NOT do**:
  - Don't change production bot settings without backup
  - Don't commit bot tokens or sensitive data

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Configuration updates based on known requirements
  - **Skills**: `[]`
    - Reason: Settings updates and OAuth testing

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 2)
  - **Blocks**: Task 4 (verification testing)
  - **Blocked By**: Task 1 (needs diagnosis results)

  **References**:

  **Pattern References** (configuration to update):
  - `celestial_insight/settings.py:196-201` - Telegram provider configuration
  - `.env:TELEGRAM_BOT_SECRET` - Bot token requiring domain match
  - `django.contrib.sites.models.Site` - Domain that must be whitelisted

  **Documentation References**:
  - Telegram OAuth docs: Domain validation requirements and setup
  - @BotFather commands: `/setdomain` and domain management
  - Callback URL format: Must match exactly what's registered with bot

  **WHY Each Reference Matters**:
  - Bot token: Must be from bot configured for correct domain
  - Domain whitelist: Telegram validates callback domain against bot settings
  - Site domain: Must match what's registered with @BotFather

  **Acceptance Criteria**:

  **Automated Verification**:
  ```bash
  # Agent verifies Telegram bot configuration
  uv run python -c "
  from django.conf import settings
  from django.contrib.sites.models import Site
  
  site = Site.objects.get(id=1)
  tg_config = settings.SOCIALACCOUNT_PROVIDERS['telegram']
  bot_id = tg_config['APP']['client_id']
  
  print(f'Site domain: {site.domain}')
  print(f'Telegram bot ID: {bot_id}')
  print(f'Expected callback: http://{site.domain}/accounts/telegram/login/callback/')
  "
  
  # Agent tests Telegram OAuth flow
  uv run python manage.py runserver --noreload &
  sleep 3
  echo "Testing Telegram OAuth flow..."
  response=$(curl -s -w "%{http_code}" -o /tmp/tg_response.html http://127.0.0.1:8000/accounts/telegram/login/)
  echo "Response status: $response"
  
  if [ "$response" = "302" ]; then
      redirect_url=$(curl -s -w "%{redirect_url}" -o /dev/null http://127.0.0.1:8000/accounts/telegram/login/)
      echo "Redirect URL: $redirect_url"
      echo "Bot domain check: $(echo $redirect_url | grep -o 'bot_id=[0-9]*' || echo 'NOT FOUND')"
  else
      echo "ERROR: Expected 302 redirect, got $response"
      head -3 /tmp/tg_response.html
  fi
  pkill -f runserver
  ```

  **Evidence to Capture**:
  - [ ] Telegram OAuth redirect URL with correct bot_id
  - [ ] Successful redirect without "Bot domain invalid" error
  - [ ] Bot domain configuration confirmation

  **Commit**: YES (if settings changes needed)
  - Message: `fix(auth): configure telegram bot domain for oauth`
  - Files: `celestial_insight/settings.py` (if needed)
  - Pre-commit: `uv run python -c "from django.conf import settings; print('Bot ID:', settings.SOCIALACCOUNT_PROVIDERS['telegram']['APP']['client_id'])"`

- [ ] 3. Fix GitHub OAuth Configuration  

  **What to do**:
  - Based on diagnosis, fix GitHub OAuth app configuration
  - Verify GitHub developer console redirect URI settings
  - Update callback URLs in GitHub OAuth app if needed
  - Test GitHub OAuth callback handling
  - Ensure complete GitHub OAuth flow works

  **Must NOT do**:
  - Don't create new GitHub OAuth apps unnecessarily
  - Don't commit GitHub client secrets

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Configuration verification and testing
  - **Skills**: `[]`
    - Reason: OAuth testing and configuration checks

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 3)
  - **Blocks**: Task 4 (comprehensive testing)
  - **Blocked By**: Task 1 (needs diagnosis), Task 2 (sequential fixes)

  **References**:

  **Pattern References** (existing configuration):
  - `celestial_insight/settings.py:182-189` - GitHub provider configuration
  - `.env:GITHUB_CLIENT_ID,GITHUB_CLIENT_SECRET` - GitHub OAuth credentials
  - `celestial_insight/urls.py:13` - GitHub callback URL pattern

  **Documentation References**:
  - GitHub OAuth app settings: Callback URL requirements and format
  - GitHub developer console: Where redirect URIs are configured
  - OAuth callback flow: How GitHub processes callback with code parameter

  **External References** (GitHub console verification):
  - GitHub Developer Settings: OAuth app redirect URI list
  - Callback URL format: `http://127.0.0.1:8000/accounts/github/login/callback/`
  - Authorization URL: GitHub OAuth authorize endpoint parameters

  **WHY Each Reference Matters**:
  - GitHub app settings: Must have exact callback URL match
  - OAuth credentials: Must be valid and correspond to correct app
  - Callback handling: Django must process GitHub's OAuth response correctly

  **Acceptance Criteria**:

  **Automated Verification**:
  ```bash
  # Agent verifies GitHub OAuth configuration
  uv run python -c "
  from django.conf import settings
  from django.contrib.sites.models import Site
  
  site = Site.objects.get(id=1)
  gh_config = settings.SOCIALACCOUNT_PROVIDERS['github']
  client_id = gh_config['APP']['client_id']
  
  print(f'Site domain: {site.domain}')
  print(f'GitHub client ID: {client_id}')
  print(f'Expected callback: http://{site.domain}/accounts/github/login/callback/')
  "
  
  # Agent tests GitHub OAuth flow initiation
  uv run python manage.py runserver --noreload &
  sleep 3
  echo "Testing GitHub OAuth flow..."
  redirect_url=$(curl -s -w "%{redirect_url}" -o /dev/null http://127.0.0.1:8000/accounts/github/login/)
  echo "GitHub redirect: $redirect_url"
  
  # Extract and verify redirect parameters
  if echo "$redirect_url" | grep -q "github.com/login/oauth/authorize"; then
      echo "✅ Redirects to GitHub OAuth"
      echo "Client ID: $(echo "$redirect_url" | grep -o 'client_id=[^&]*' | cut -d= -f2)"
      echo "Callback URL: $(echo "$redirect_url" | grep -o 'redirect_uri=[^&]*' | cut -d= -f2 | python -c 'import sys, urllib.parse; print(urllib.parse.unquote(sys.stdin.read()))')"
  else
      echo "❌ Invalid GitHub OAuth redirect"
  fi
  pkill -f runserver
  
  # Agent tests callback URL accessibility  
  uv run python manage.py shell -c "
  from django.test import Client
  client = Client()
  
  # Test callback URL with dummy parameters
  response = client.get('/accounts/github/login/callback/?code=test&state=test')
  print(f'Callback status: {response.status_code}')
  print(f'Callback handles request: {response.status_code != 404}')
  "
  ```

  **Evidence to Capture**:
  - [ ] GitHub OAuth redirect URL with correct parameters
  - [ ] Callback URL accessibility confirmation
  - [ ] GitHub OAuth app configuration verification

  **Commit**: YES (if fixes needed)
  - Message: `fix(auth): correct github oauth callback configuration`
  - Files: Configuration files if updated
  - Pre-commit: `curl -s -w "%{http_code}" -o /dev/null http://127.0.0.1:8000/accounts/github/login/ | grep -q "302" && echo "OK"`

- [ ] 4. Comprehensive OAuth Testing

  **What to do**:
  - Test all OAuth flows end-to-end with browser automation
  - Verify user creation and login works for each provider
  - Test OAuth error handling and edge cases
  - Document working OAuth configurations
  - Capture evidence of successful OAuth flows

  **Must NOT do**:
  - Don't modify configurations during testing
  - Don't commit test artifacts or temporary files

  **Recommended Agent Profile**:
  - **Category**: `visual-engineering`
    - Reason: Requires browser automation to test complete OAuth flows
  - **Skills**: `["dev-browser"]`
    - Reason: OAuth testing requires navigating to external providers

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Sequential (Task 4 - Final)
  - **Blocks**: None (final verification task)
  - **Blocked By**: Tasks 1, 2, 3 (needs all fixes complete)

  **References**:

  **Pattern References** (OAuth flow verification):
  - `templates/account/login.html` - Social auth buttons and UI
  - `users/adapters.py:pre_social_login()` - Custom account merging logic
  - `celestial_insight/settings.py:181-201` - Final OAuth configurations

  **Test References** (complete flow verification):
  - OAuth initiation: Click social login buttons
  - Provider redirect: Verify external OAuth pages load
  - Callback handling: Ensure successful return to application
  - User creation: Verify user accounts are created/linked

  **Evidence References** (documentation patterns):
  - Screenshots: OAuth flow working end-to-end
  - Logs: Successful OAuth callback processing
  - Database: User and social account creation

  **WHY Each Reference Matters**:
  - Login UI: Shows OAuth options are properly displayed
  - Account adapter: Critical for linking OAuth accounts to users
  - Complete flow: Proves OAuth integration works for real users

  **Acceptance Criteria**:

  **Automated Verification (Browser Testing)**:
  ```bash
  # Agent starts development server for testing
  uv run python manage.py runserver --noreload &
  SERVER_PID=$!
  sleep 5
  
  # Browser automation test (via dev-browser skill):
  # 1. Navigate to login page
  # 2. Verify GitHub and Telegram social login buttons are present
  # 3. Test GitHub OAuth initiation (redirects to github.com)
  # 4. Test Telegram OAuth initiation (redirects to oauth.telegram.org)
  # 5. Verify no "Bot domain invalid" errors for Telegram
  # 6. Screenshot evidence of working OAuth initiation
  
  # Cleanup
  kill $SERVER_PID
  ```

  **For OAuth Flow Verification** (using Django commands):
  ```bash
  # Agent verifies OAuth provider configurations
  uv run python manage.py shell -c "
  from django.contrib.sites.models import Site
  from django.conf import settings
  from django.urls import reverse
  
  site = Site.objects.get(id=1)
  print(f'Site domain: {site.domain}')
  print(f'Site configured: {site.domain == \"127.0.0.1:8000\"}')
  
  providers = ['github', 'telegram']
  for provider in providers:
      try:
          login_url = reverse(f'{provider}_login')
          callback_url = reverse(f'{provider}_callback')
          config = settings.SOCIALACCOUNT_PROVIDERS[provider]['APP']
          
          print(f'\\n{provider.upper()} Configuration:')
          print(f'  Login URL: {login_url}')
          print(f'  Callback URL: {callback_url}')
          print(f'  Client ID: {config[\"client_id\"][:20]}...')
          print(f'  Full callback: http://{site.domain}{callback_url}')
      except Exception as e:
          print(f'{provider}: ERROR - {e}')
  "
  # Assert: All providers configured correctly
  ```

  **Evidence to Capture**:
  - [ ] Screenshot of login page with working OAuth buttons (.sisyphus/evidence/oauth-login-working.png)
  - [ ] Screenshot of GitHub OAuth redirect (.sisyphus/evidence/github-oauth-working.png)  
  - [ ] Screenshot of Telegram OAuth redirect (.sisyphus/evidence/telegram-oauth-working.png)
  - [ ] Terminal output showing successful OAuth configurations
  - [ ] Confirmation that "Bot domain invalid" error is resolved

  **Commit**: NO
  - This is verification only, no code changes

---

## Success Criteria

### Verification Commands
```bash
# Test GitHub OAuth flow
curl -s -w "GitHub: %{http_code} -> %{redirect_url}\n" -o /dev/null http://127.0.0.1:8000/accounts/github/login/  # Expected: 302 -> github.com

# Test Telegram OAuth flow  
curl -s -w "Telegram: %{http_code} -> %{redirect_url}\n" -o /dev/null http://127.0.0.1:8000/accounts/telegram/login/  # Expected: 302 -> oauth.telegram.org (no domain error)

# Verify callback URLs resolve
uv run python manage.py shell -c "from django.urls import reverse; print('GitHub callback:', reverse('github_callback')); print('Telegram callback:', reverse('telegram_callback'))"  # Expected: Both resolve

# Verify Site domain configuration
uv run python manage.py shell -c "from django.contrib.sites.models import Site; print('Site domain:', Site.objects.get(id=1).domain)"  # Expected: 127.0.0.1:8000
```

### Final Checklist
- [ ] Telegram OAuth completes without "Bot domain invalid" error
- [ ] GitHub OAuth flow works end-to-end
- [ ] No OAuth domain validation errors
- [ ] All callback URLs properly configured in provider consoles
- [ ] OAuth redirect URLs match provider app configurations