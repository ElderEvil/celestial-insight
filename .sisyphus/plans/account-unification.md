# Account Unification: Email Bridge + Social Auth

## TL;DR

> **Quick Summary**: Enable account unification between Telegram bot and web UI using email bridging and social authentication (Google/GitHub).
> 
> **Deliverables**: Unified user accounts across interfaces
> - Telegram `/email` command to set email address
> - Enable Google/GitHub login buttons (already configured!)
> - Auto-merge accounts on web signup when email matches
> - Preserve tokens and reading history during account merging
> 
> **Estimated Effort**: Short
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Email command → Social auth → Auto-merge

---

## Context

### Original Request
User wants account unification between Telegram bot and web UI, starting with email bridging and expanding to social authentication providers.

### Interview Summary
**Key Discussions**:
- **Email Bridge**: Telegram users add email via bot command, web users sign in with same email
- **Social Auth**: Enable existing Google/GitHub providers (already configured)
- **Auto-Linking**: Automatically merge accounts when web signup email matches Telegram user
- **Skip Features**: Account management page, QR code linking (not needed initially)

**Research Findings**:
- **Foundation Exists**: Django-Allauth fully configured with Google/GitHub providers
- **Current State**: Social login disabled via `SOCIALACCOUNT_LOGIN_ON = False`
- **Templates Ready**: Social login buttons already exist in `templates/socialaccount/`
- **Architecture**: Session-based web auth + JWT API auth + Telegram SocialAccount pattern

### Metis Review
**Identified Gaps** (addressed):
- **Email Verification**: Use current setting (none) for simplicity
- **Account Merging Logic**: Primary account = first created, preserve tokens/history
- **Conflict Resolution**: Primary account wins for conflicting data
- **Frontend Technology**: HTMX + Django templates (no React/Vue)

---

## Work Objectives

### Core Objective
Enable seamless account unification between Telegram bot and web UI using email bridging and social authentication.

### Concrete Deliverables
- `/email` command in Telegram bot for setting user email
- Enabled Google/GitHub login buttons on web UI
- Auto-merge logic for web signup when email matches Telegram user
- Unified token balance across all interfaces

### Definition of Done
- [ ] Telegram users can set email via `/email` command
- [ ] Web UI shows Google/GitHub login buttons
- [ ] Web signup merges with existing Telegram account if email matches
- [ ] Token balance shared across Telegram and web interfaces
- [ ] Reading history preserved during account merging

### Must Have
- Email bridging functionality working
- Social auth providers enabled and functional
- Account merging preserves user data
- No duplicate accounts created

### Must NOT Have (Guardrails)
- **No email verification required** - Keep current setting for simplicity
- **No account unlinking** - Not needed in Phase 1
- **No complex conflict resolution** - Primary account wins
- **No breaking changes to existing auth** - Extend, don't replace

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (Django test framework)
- **User wants tests**: Manual verification
- **Framework**: Django test framework + manual testing
- **QA approach**: Manual verification with HTMX interactions

### Manual Verification Only

Each TODO includes EXECUTABLE verification procedures that agents can run directly:

**For Telegram Bot Commands** (using interactive_bash for tmux):
```bash
# Agent tests /email command:
python bot.py  # Start bot
# Simulate /email command via webhook POST
curl -X POST "http://localhost:8080/webhook" -H "Content-Type: application/json" \
  -d '{"message":{"text":"/email test@example.com","from":{"id":382660930,"username":"elder_evil_tg"}}}'
# Verify email stored in database
```

**For Web UI** (using playwright skill):
```
# Agent tests via browser automation:
1. Navigate to: http://localhost:8000/accounts/login/
2. Assert: Google and GitHub login buttons visible
3. Click: "Sign in with Google" button
4. Assert: OAuth redirect happens (or mock in tests)
5. Screenshot: .sisyphus/evidence/social-login-buttons.png
```

**For API Integration** (using Bash curl):
```bash
# Agent tests account merge:
# Create web user
curl -s -X POST "http://localhost:8000/api/accounts/signup/" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'

# Check if user was merged with existing Telegram account
curl -s "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer <token>" | jq '.profile.available_tokens'
# Assert: Shows combined token balance
```

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately):
├── Task 1: Add /email command to Telegram bot (no dependencies)
└── Task 2: Enable social auth in settings (no dependencies)

Wave 2 (After Wave 1):
├── Task 3: Auto-merge on web signup (depends: 1)
└── Task 4: Update Telegram auth to check existing emails (depends: 1)

Wave 3 (After Wave 2):
└── Task 5: Test full unification flow (depends: 3, 4)

Critical Path: Task 1 → Task 3 → Task 5
Parallel Speedup: ~30% faster than sequential
```

### Dependency Matrix

| Task | Depends On | Blocks | Can Parallelize With |
|------|------------|--------|---------------------|
| 1 | None | 3, 4 | 2 |
| 2 | None | None | 1 |
| 3 | 1 | 5 | 4 |
| 4 | 1 | 5 | 3 |
| 5 | 3, 4 | None | None (final) |

### Agent Dispatch Summary

| Wave | Tasks | Recommended Agents |
|------|-------|-------------------|
| 1 | 1, 2 | delegate_task(category="quick", load_skills=["git-master"], run_in_background=true) |
| 2 | 3, 4 | dispatch parallel after Wave 1 completes |
| 3 | 5 | final integration testing |

---

## TODOs

- [ ] 1. Add /email Command to Telegram Bot

  **What to do**:
  - Add `/email` command handler to `bot.py`
  - Validate email format using Python email validation
  - Update User.email field via API call to `/api/users/update-email`
  - Show confirmation message with current/new email
  - Handle cases where email is already in use

  **Must NOT do**:
  - Add email verification (keep simple for Phase 1)
  - Change existing auth flows
  - Modify other bot commands

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple command addition, clear pattern to follow
  - **Skills**: [`git-master`]
    - `git-master`: Need organized commit for new feature

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 2)
  - **Blocks**: Task 3, 4 (need email setting capability)
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (existing code to follow):
  - `bot.py:228-255` - Command handler pattern for `/mentors` 
  - `bot.py:461-477` - CommandHandler registration pattern
  - `users/api.py:39-77` - User update patterns via API

  **Validation References**:
  - Python standard library: `email.utils.parseaddr` for email validation
  - Django pattern: Use email validation from `django.core.validators`

  **API References** (new endpoint needed):
  - **NEW ENDPOINT**: `PATCH /api/users/update-email` - Update user email
  - `users/schemas.py` - Define EmailUpdateSchema for request validation

  **WHY Each Reference Matters**:
  - Command pattern shows exact structure for new `/email` command
  - API patterns show how to make authenticated PATCH requests
  - Validation patterns ensure email format is correct before API call

  **Acceptance Criteria**:

  **Manual Verification**:
  ```bash
  # Agent tests email command via bot simulation:
  python -c "
  import os
  os.environ['TELEGRAM_BOT_SECRET'] = 'test'
  os.environ['API_URL'] = 'http://localhost:8000'
  import asyncio
  from unittest.mock import MagicMock
  from bot import BotHandlers
  
  handler = BotHandlers('http://localhost:8000')
  update = MagicMock()
  update.message.from_user.id = 382660930
  update.message.text = '/email test@example.com'
  
  # This should validate email format
  result = asyncio.run(handler.handle_email_command(update, None))
  print('Email validation test completed')
  "
  ```

  **Evidence to Capture**:
  - [ ] Email validation working for valid emails
  - [ ] Error handling for invalid email formats
  - [ ] API integration for updating user email

  **Commit**: YES
  - Message: `feat(bot): add /email command for account linking`
  - Files: `bot.py`, `users/api.py`, `users/schemas.py`
  - Pre-commit: `uv run python -c "from bot import BotHandlers; print('imports ok')"`

- [ ] 2. Enable Social Auth in Settings

  **What to do**:
  - Change `SOCIALACCOUNT_LOGIN_ON = False` to `True` in `celestial_insight/settings.py`
  - Verify Google and GitHub client_id/secret are set in environment
  - Test that social login buttons appear on `/accounts/login/`
  - Ensure existing templates work with enabled social auth

  **Must NOT do**:
  - Change any template files (they already exist)
  - Modify allauth configuration beyond enabling
  - Add new social providers

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Single setting change, templates already exist
  - **Skills**: [`git-master`]
    - `git-master`: Clean commit for configuration change

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: None (independent setting change)
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (existing configuration):
  - `celestial_insight/settings.py:169` - Current `SOCIALACCOUNT_LOGIN_ON = False`
  - `celestial_insight/settings.py:173-180` - Existing provider configuration

  **Template References** (already exist):
  - `templates/socialaccount/provider_list.html` - Social login buttons
  - `templates/account/login.html` - Login form where buttons will appear

  **Environment References**:
  - `.env` file should have `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
  - `.env` file should have `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`

  **WHY Each Reference Matters**:
  - Setting controls whether social buttons show on forms
  - Templates already designed to work when social auth is enabled
  - Environment variables must be set for OAuth to work

  **Acceptance Criteria**:

  **Manual Verification**:
  ```bash
  # Agent verifies social login buttons appear:
  # Start Django server
  uv run python manage.py runserver &
  SERVER_PID=$!
  sleep 3

  # Check login page has social buttons
  curl -s http://localhost:8000/accounts/login/ | grep -E "(Sign in with Google|Sign in with GitHub)"
  # Assert: Social login buttons found in HTML

  # Cleanup
  kill $SERVER_PID
  ```

  **Evidence to Capture**:
  - [ ] SOCIALACCOUNT_LOGIN_ON changed to True
  - [ ] Social login buttons visible on login page
  - [ ] Environment variables configured for OAuth

  **Commit**: YES
  - Message: `feat(auth): enable Google/GitHub social login buttons`
  - Files: `celestial_insight/settings.py`
  - Pre-commit: `uv run python manage.py check`

- [ ] 3. Auto-Link on Web Signup

  **What to do**:
  - Create custom allauth adapter in `users/adapters.py`
  - Override `pre_social_login` method to check for existing Telegram users
  - If web signup email matches Telegram user email, merge accounts
  - Preserve token balance and reading history from Telegram account
  - Add logic to `users/api.py` for account merging

  **Must NOT do**:
  - Create duplicate users with same email
  - Lose token balance during merge
  - Break existing authentication flows

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: Account merging logic requires careful handling
  - **Skills**: [`git-master`]
    - `git-master`: Need careful commits for auth changes

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 4)
  - **Parallel Group**: Wave 2 (with Task 4)
  - **Blocks**: Task 5 (final testing)
  - **Blocked By**: Task 1 (needs email command working)

  **References**:

  **Pattern References** (Django-Allauth patterns):
  - Django-Allauth docs: Custom adapter for `pre_social_login` override
  - `users/api.py:48-67` - Existing SocialAccount creation pattern

  **Account Merging References**:
  - Django `User.objects.filter(email=...)` - Find users by email
  - `SocialAccount.objects.filter(user=...)` - Check existing social accounts
  - `UserProfile.objects.get(user=...)` - Access token balance

  **Database References**:
  - `users/models.py:11-22` - UserProfile structure (tokens, preferences)
  - `allauth.socialaccount.models.SocialAccount` - Social account linking

  **WHY Each Reference Matters**:
  - Allauth adapter pattern provides the hook for custom merge logic
  - Existing SocialAccount pattern shows how accounts are linked
  - UserProfile shows what data needs to be preserved during merge

  **Acceptance Criteria**:

  **Manual Verification**:
  ```bash
  # Agent tests account merge:
  # 1. Create Telegram user with email via bot
  # 2. Try to signup on web with same email
  # 3. Verify accounts are merged, not duplicated
  
  # Check no duplicate users
  uv run python manage.py shell -c "
  from django.contrib.auth.models import User
  from allauth.socialaccount.models import SocialAccount
  
  test_email = 'test@example.com'
  users = User.objects.filter(email=test_email)
  print(f'Users with {test_email}: {users.count()}')
  # Assert: Should be 1, not 2
  
  if users.exists():
      user = users.first()
      accounts = SocialAccount.objects.filter(user=user)
      print(f'Social accounts: {[acc.provider for acc in accounts]}')
      # Assert: Should include 'telegram' and others
  "
  ```

  **Evidence to Capture**:
  - [ ] Custom allauth adapter created and configured
  - [ ] Account merge working without duplicates
  - [ ] Token balance preserved during merge

  **Commit**: YES
  - Message: `feat(auth): add auto-merge for web signup with existing Telegram users`
  - Files: `users/adapters.py`, `celestial_insight/settings.py`
  - Pre-commit: `uv run python manage.py check`

- [ ] 4. Update Telegram Auth to Check Existing Emails

  **What to do**:
  - Modify `/api/tg/users/auth` endpoint in `users/api.py`
  - Before creating new SocialAccount, check if User with telegram username already exists from web signup
  - If found, link the Telegram social account to existing User
  - If not found, proceed with current flow (create new user)
  - Ensure token balance is preserved correctly

  **Must NOT do**:
  - Break existing Telegram authentication
  - Create duplicate social accounts
  - Lose token data during linking

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Extending existing auth logic, clear pattern
  - **Skills**: [`git-master`]
    - `git-master`: Careful commits for authentication changes

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 3)
  - **Parallel Group**: Wave 2 (with Task 3)
  - **Blocks**: Task 5 (final testing)
  - **Blocked By**: Task 1 (needs email command for full flow)

  **References**:

  **Pattern References** (existing code to extend):
  - `users/api.py:48-67` - Current Telegram auth creation flow
  - `users/api.py:56-57` - User creation with username pattern

  **Lookup References**:
  - `User.objects.filter(email=...)` - Find existing user by email
  - `User.objects.filter(username=...)` - Find existing user by username
  - `SocialAccount.objects.filter(user=..., provider="telegram")` - Check existing Telegram links

  **Account Linking References**:
  - `SocialAccount.objects.create(user=existing_user, provider="telegram", uid=telegram_id)`
  - Pattern: Link to existing user instead of creating new

  **WHY Each Reference Matters**:
  - Current auth flow shows exact logic to extend
  - User lookup patterns show how to find existing accounts
  - SocialAccount creation shows how to link instead of duplicating

  **Acceptance Criteria**:

  **Manual Verification**:
  ```bash
  # Agent tests Telegram auth with existing web user:
  
  # Create web user first (simulate)
  uv run python manage.py shell -c "
  from django.contrib.auth.models import User
  user, created = User.objects.get_or_create(
      email='test@example.com',
      defaults={'username': 'webuser'}
  )
  print(f'Web user created: {created}, ID: {user.id}')
  "
  
  # Now test Telegram auth for same email
  curl -s -X POST "http://localhost:8000/api/tg/users/auth" \
    -H "Content-Type: application/json" \
    -d '{"telegram_id": 999999, "username": "test@example.com"}' | jq '.username'
  # Assert: Should link to existing web user, not create new
  ```

  **Evidence to Capture**:
  - [ ] Telegram auth links to existing web users
  - [ ] No duplicate accounts created
  - [ ] Token balance preserved correctly

  **Commit**: YES
  - Message: `feat(auth): link Telegram accounts to existing web users by email`
  - Files: `users/api.py`
  - Pre-commit: `curl localhost:8000/api/tg/users/auth | jq`

- [ ] 5. Test Full Unification Flow

  **What to do**:
  - Create comprehensive test of the full account unification flow
  - Test scenario: Telegram user → Set email → Web signup → Verify unified account
  - Verify token balance sharing across interfaces
  - Test social login (Google/GitHub) integration
  - Document the complete user journey

  **Must NOT do**:
  - Skip edge case testing
  - Deploy without verification
  - Leave broken auth flows

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: Integration testing requires thorough verification
  - **Skills**: [`git-master`]
    - `git-master`: Final verification commit

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (final integration)
  - **Blocks**: None (final task)
  - **Blocked By**: Task 3, 4 (needs merge logic working)

  **References**:

  **Test Pattern References**:
  - `users/tests/test_telegram_auth.py` - Existing Telegram auth test patterns
  - Django testing: `self.client.post('/accounts/login/')` for web auth testing

  **Integration Points**:
  - Bot command: `/email` → API: `PATCH /api/users/update-email`
  - Web signup: `/accounts/signup/` → Merge check via custom adapter
  - Social login: `/accounts/google/login/` → Account linking

  **Verification Commands**:
  - `uv run python bot.py` - Start Telegram bot
  - `uv run python manage.py runserver` - Start web server
  - Manual testing via Telegram app + browser

  **WHY Each Reference Matters**:
  - Test patterns show how to verify auth flows end-to-end
  - Integration points show where the unification logic connects
  - Manual testing ensures real-world UX works correctly

  **Acceptance Criteria**:

  **Integration Testing**:
  ```bash
  # Agent runs full integration test:
  
  # Start services
  uv run python manage.py runserver &
  WEB_PID=$!
  python bot.py &
  BOT_PID=$!
  sleep 3
  
  # Test complete flow
  echo "Testing account unification flow..."
  
  # 1. Telegram user sets email
  # 2. Web user signs up with same email
  # 3. Verify unified account
  
  # Check unified user exists
  uv run python manage.py shell -c "
  from django.contrib.auth.models import User
  from allauth.socialaccount.models import SocialAccount
  
  user = User.objects.filter(email='test@example.com').first()
  if user:
      accounts = SocialAccount.objects.filter(user=user)
      print(f'Unified user: {user.username}')
      print(f'Linked accounts: {[acc.provider for acc in accounts]}')
      print(f'Token balance: {user.profile.available_tokens}')
  "
  
  # Cleanup
  kill $WEB_PID $BOT_PID
  ```

  **Evidence to Capture**:
  - [ ] Full unification flow working end-to-end
  - [ ] Token balance shared across interfaces
  - [ ] Social login integration working
  - [ ] No duplicate accounts created during testing

  **Commit**: YES
  - Message: `test(auth): verify complete account unification flow`
  - Files: Documentation or test files
  - Pre-commit: `uv run pytest users/tests/`

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `feat(bot): add /email command for account linking` | bot.py, users/api.py, users/schemas.py | Email validation |
| 2 | `feat(auth): enable Google/GitHub social login buttons` | settings.py | Social buttons |
| 3 | `feat(auth): add auto-merge for web signup with existing Telegram users` | users/adapters.py, settings.py | Account merge |
| 4 | `feat(auth): link Telegram accounts to existing web users by email` | users/api.py | Telegram linking |
| 5 | `test(auth): verify complete account unification flow` | tests/ | Integration |

---

## Success Criteria

### Verification Commands
```bash
uv run python manage.py runserver  # Expected: Web server starts
python bot.py  # Expected: Bot starts with /email command
```

### Final User Flows

**Flow 1: Telegram → Web Unification**
1. User uses Telegram bot → `/email user@example.com`
2. Bot: "✅ Email set to user@example.com"
3. User goes to web UI → Sign up with same email
4. System: Auto-merges accounts, preserves tokens
5. User has unified access to both interfaces

**Flow 2: Web → Social Auth**
1. User goes to `/accounts/login/`
2. Sees: Email login + Google/GitHub buttons
3. Clicks social provider → OAuth flow
4. Returns with linked account

**Flow 3: Telegram → Web Social**
1. Telegram user sets email via `/email`
2. Web user signs up with Google (same email)
3. System detects matching email and merges
4. Unified account with Telegram + Google providers

### Final Checklist
- [ ] `/email` command works in Telegram bot
- [ ] Google/GitHub buttons visible on web login
- [ ] Web signup merges with Telegram accounts by email
- [ ] Token balance shared across all interfaces
- [ ] Reading history preserved during merging