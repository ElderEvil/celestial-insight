# Fix Telegram Bot Integration Issues

## TL;DR

> **Quick Summary**: Fix critical Telegram bot crashes and authentication issues, add simplified auth for bot endpoints, and improve error handling.
> 
> **Deliverables**: Working Telegram bot with fixed response parsing, simplified authentication, improved error handling, and proper API integration
> - Fixed `/mentors` command crash
> - Working authentication flow
> - Simplified bot-specific API endpoints
> - Comprehensive error handling
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Fix bot crash → Test auth → Add error handling

---

## Context

### Original Request
User reported Telegram bot crashes with error: `'list' object has no attribute 'get'` when using `/mentors` command, plus authentication failures and validation errors.

### Interview Summary
**Key Discussions**:
- **Priority**: Fix + Improve - comprehensive fixes with better error handling
- **Auth Strategy**: Simplified Auth - use simpler mechanism than JWT for bot endpoints
- **Scope**: Fix all bot integration issues, add resilience

**Research Findings**:
- Bot code assumes API returns `{"results": [...]}` but APIs return `[...]` directly
- Authentication token extraction is incorrect in bot code
- Multiple response format mismatches between bot expectations and actual API responses
- Missing username field in some auth requests

### Metis Review
**Identified Gaps** (addressed):
- **Critical Auth Bug**: Bot extracts token from non-existent "tokens" key instead of direct "access" field
- **Dual Bot Files**: Both `bot.py` and `run_bot.py` need fixes but have different issues
- **Missing Endpoints**: Bot needs simplified `/me` endpoint that works with telegram_id instead of JWT
- **Missing Required Fields**: Bot doesn't send required `mentor_id` for reading creation
- **Error Handling**: No handling for non-200 API responses

---

## Work Objectives

### Core Objective
Fix all Telegram bot integration issues to restore functionality and add resilience against API failures.

### Concrete Deliverables
- Working `/mentors` command without crashes
- Functional authentication flow for all bot commands
- Simplified Telegram-specific API endpoints
- Comprehensive error handling and logging
- Updated bot response parsing for correct API formats

### Definition of Done
- [ ] `python bot.py` starts without errors
- [ ] All Telegram commands work without crashes
- [ ] Authentication flow succeeds for all protected operations
- [ ] Bot gracefully handles API failures with user-friendly messages

### Must Have
- Fix immediate bot crash in `/mentors` command
- Correct authentication token extraction
- Add simplified auth endpoints for Telegram bot
- Fix all response format mismatches

### Must NOT Have (Guardrails)
- **No complex JWT flow for bot endpoints** - Keep JWT for web, use simplified for bot
- **No breaking changes to existing web API** - Only add new Telegram-specific endpoints
- **No over-engineering** - Fix what's broken, don't rebuild the entire system
- **No untested changes** - Every fix must be verifiable

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO (only basic project structure)
- **User wants tests**: Manual-only
- **Framework**: Manual verification with bot commands
- **QA approach**: Manual verification

### Automated Verification Only

Each TODO includes EXECUTABLE verification procedures that agents can run directly:

**For Bot Commands** (using interactive_bash for tmux):
```bash
# Agent executes via tmux session:
1. Start bot: python bot.py
2. Send test message via curl to Telegram API
3. Check bot logs for errors
4. Verify expected responses
```

**For API Endpoints** (using Bash curl):
```bash
# Agent runs:
curl -s -X GET http://localhost:8000/api/mentors/ | jq 'type'
# Assert: Returns "array"

curl -s -X POST http://localhost:8000/api/tg/users/auth \
  -H "Content-Type: application/json" \
  -d '{"telegram_id":12345,"username":"test"}' | jq '.access'
# Assert: Returns non-empty string
```

**Evidence Requirements (Agent-Executable):**
- Terminal output from bot startup and command handling
- API response validation via curl
- Bot log analysis for error patterns

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately):
├── Task 1: Fix bot response parsing (no dependencies)
└── Task 4: Add simplified auth endpoints (no dependencies)

Wave 2 (After Wave 1):
├── Task 2: Fix authentication token extraction (depends: 4)
└── Task 5: Add error handling (depends: 1)

Wave 3 (After Wave 2):
└── Task 3: Test full integration (depends: 2, 5)

Critical Path: Task 1 → Task 2 → Task 3
Parallel Speedup: ~30% faster than sequential
```

### Dependency Matrix

| Task | Depends On | Blocks | Can Parallelize With |
|------|------------|--------|---------------------|
| 1 | None | 2, 5 | 4 |
| 2 | 1, 4 | 3 | 5 |
| 3 | 2, 5 | None | None (final) |
| 4 | None | 2 | 1 |
| 5 | 1 | 3 | 2 |

### Agent Dispatch Summary

| Wave | Tasks | Recommended Agents |
|------|-------|-------------------|
| 1 | 1, 4 | delegate_task(category="quick", load_skills=["git-master"], run_in_background=true) |
| 2 | 2, 5 | dispatch parallel after Wave 1 completes |
| 3 | 3 | final integration verification |

---

## TODOs

- [ ] 1. Fix Bot Response Parsing Issues

  **What to do**:
  - Fix `list_mentors` method in `bot.py` to handle list responses correctly
  - Fix `list_suit_cards` method to use proper response format
  - Fix `run_bot.py` command to match `bot.py` fixes (both files need updates)
  - Remove incorrect assumptions about `{"results": [...]}` wrapper

  **Must NOT do**:
  - Break existing API response formats for web clients
  - Change API schemas - only fix client-side parsing

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Straightforward parsing fixes, clear pattern to follow
  - **Skills**: [`git-master`]
    - `git-master`: Need atomic commits for each file fix
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: No UI work involved, pure data parsing

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 4)
  - **Blocks**: Tasks 2, 5 (need working response parsing)
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (existing code to follow):
  - `bot.py:158-159` - Current handling pattern for list vs dict responses
  - `bot.py:115-117` - Shows incorrect assumption about "results" wrapper

  **API References** (contracts to understand):
  - `mentors/api.py:13-22` - Returns `list[MentorSchema]` directly, not wrapped
  - `tarot/api.py:31-33` - Returns `list[CardSchemaShort]` directly
  - `mentors/schemas.py:7-15` - Structure of individual mentor objects

  **Test References** (verification patterns):
  - Manual testing: `/mentors` command should list mentors without crashing
  - API verification: `curl localhost:8000/api/mentors/` returns array

  **WHY Each Reference Matters**:
  - `bot.py` patterns show where list/dict handling already works vs breaks
  - API files show actual return types - no "results" wrapper exists
  - Schemas show structure for proper field access

  **Acceptance Criteria**:

  **Automated Verification**:
  ```bash
  # Agent runs:
  curl -s http://localhost:8000/api/mentors/ | jq 'type'
  # Assert: Output is "array"
  
  python -c "
  import asyncio
  import sys
  sys.path.append('.')
  from bot import BotHandlers
  
  async def test():
      handler = BotHandlers('http://localhost:8000')
      mentors = await handler.fetch_data('/api/mentors/')
      print('Type:', type(mentors))
      print('Is list:', isinstance(mentors, list))
      if mentors and len(mentors) > 0:
          print('First mentor has name:', 'name' in mentors[0])
  
  asyncio.run(test())
  "
  # Assert: Output shows "Is list: True" and "First mentor has name: True"
  ```

  **Evidence to Capture**:
  - [ ] API response type verification (curl output)
  - [ ] Python type checking output
  - [ ] Bot command test results

  **Commit**: YES
  - Message: `fix(bot): correct API response parsing for lists`
  - Files: `bot.py`, `tarot/management/commands/run_bot.py`
  - Pre-commit: `curl localhost:8000/api/mentors/ | jq type`

- [ ] 2. Fix Authentication Token Extraction

  **What to do**:
  - Change `auth.get("tokens", {}).get("access")` to `auth.get("access")` in `bot.py:235`
  - Apply same fix to `run_bot.py:277-278`
  - Add proper null checking for auth responses
  - Ensure username is included in all auth requests

  **Must NOT do**:
  - Change the API response format - only fix client extraction
  - Break existing JWT token structure for web clients

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Direct field access fix, clear pattern to implement
  - **Skills**: [`git-master`]
    - `git-master`: Need careful commit of auth fixes
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: No UI work, pure data access logic

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (sequential)
  - **Blocks**: Task 3 (integration testing)
  - **Blocked By**: Tasks 1, 4 (need working parsing and auth endpoints)

  **References**:

  **Pattern References** (existing code to follow):
  - `users/api.py:73-78` - Actual token response structure without "tokens" wrapper
  - `bot.py:234-236` - Current incorrect token extraction pattern

  **API References** (contracts to implement against):
  - `users/schemas.py:23-28` - `TokenResponseSchema` shows direct fields
  - `users/api.py:40-78` - Shows exact response from `/auth` endpoint

  **Test References** (verification patterns):
  - Test auth flow: Should get access token for valid telegram_id + username
  - Manual verification: Bot commands requiring auth should work

  **WHY Each Reference Matters**:
  - `users/api.py` shows the ACTUAL response structure - no nesting exists
  - `TokenResponseSchema` defines the contract - direct fields only
  - Bot code shows where incorrect assumptions break token access

  **Acceptance Criteria**:

  **Automated Verification**:
  ```bash
  # Agent runs:
  curl -s -X POST http://localhost:8000/api/tg/users/auth \
    -H "Content-Type: application/json" \
    -d '{"telegram_id":12345,"username":"testuser"}' | jq '.access'
  # Assert: Returns non-null string token
  
  python -c "
  import asyncio
  import sys
  sys.path.append('.')
  from bot import BotHandlers
  
  async def test():
      handler = BotHandlers('http://localhost:8000')
      auth = await handler.post_request('/api/tg/users/auth', {
          'telegram_id': 12345, 'username': 'testuser'
      })
      if auth:
          access = auth.get('access')
          print('Access token exists:', access is not None)
          print('Token starts with:', access[:10] if access else 'None')
      else:
          print('Auth failed')
  
  asyncio.run(test())
  "
  # Assert: Shows "Access token exists: True"
  ```

  **Evidence to Capture**:
  - [ ] Successful auth API response
  - [ ] Token extraction verification
  - [ ] Bot auth flow test results

  **Commit**: YES
  - Message: `fix(bot): correct JWT token extraction from auth response`
  - Files: `bot.py`, `tarot/management/commands/run_bot.py`
  - Pre-commit: `curl -X POST localhost:8000/api/tg/users/auth -d '{"telegram_id":1,"username":"test"}' | jq .access`

- [ ] 3. Test Full Bot Integration

  **What to do**:
  - Start Django development server
  - Start bot with test Telegram token
  - Test all commands: `/start`, `/mentors`, `/me`, `/reading`, `/history`
  - Verify authentication flow works end-to-end
  - Test error conditions and graceful handling

  **Must NOT do**:
  - Use production Telegram token in tests
  - Test against production Django instance

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Testing existing functionality, straightforward verification
  - **Skills**: [`git-master`]
    - `git-master`: May need to commit test results or final adjustments
  - **Skills Evaluated but Omitted**:
    - `playwright`: No web browser testing needed, pure API/bot testing

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (final verification)
  - **Blocks**: None (final task)
  - **Blocked By**: Tasks 2, 5 (need working auth and error handling)

  **References**:

  **Pattern References** (existing code to follow):
  - `bot.py:77-90` - Start command flow for testing pattern
  - `bot.py:305-324` - Command registration pattern to verify

  **API References** (endpoints to verify):
  - All `/api/mentors/`, `/api/tg/users/auth`, `/api/tg/users/me` endpoints
  - Simplified auth endpoints from Task 4

  **Test References** (verification procedures):
  - Manual bot command testing via Telegram interface
  - Simulated webhook testing for Telegram updates

  **WHY Each Reference Matters**:
  - Bot command flows show expected behavior patterns
  - API endpoints define integration points to test
  - Full integration validates all previous fixes work together

  **Acceptance Criteria**:

  **Automated Verification**:
  ```bash
  # Agent executes via tmux session:
  # Terminal 1: Start Django server
  uv run python manage.py runserver &
  sleep 3
  
  # Terminal 2: Test bot startup
  python -c "
  import os
  os.environ['TELEGRAM_BOT_SECRET'] = 'test_token'
  os.environ['API_URL'] = 'http://localhost:8000'
  from bot import main
  print('Bot configuration valid')
  "
  # Assert: No import errors or configuration issues
  
  # Test API integration
  curl -s http://localhost:8000/api/mentors/ | jq 'length'
  # Assert: Returns number > 0 (mentors exist)
  ```

  **Evidence to Capture**:
  - [ ] Bot startup logs without errors
  - [ ] Successful command response simulation
  - [ ] API endpoint integration verification

  **Commit**: YES
  - Message: `test(bot): verify complete Telegram integration`
  - Files: Test logs, verification scripts
  - Pre-commit: `uv run python manage.py check`

- [ ] 4. Add Simplified Telegram Auth Endpoints

  **What to do**:
  - Add new `/api/tg/users/me` endpoint that works with `?telegram_id=X` parameter
  - Create simple auth mechanism for Telegram bot (API key or token-based)
  - Update bot to use simplified endpoints instead of complex JWT flow
  - Ensure backwards compatibility with existing JWT endpoints

  **Must NOT do**:
  - Remove or break existing JWT authentication for web clients
  - Create security vulnerabilities with overly simple auth
  - Expose sensitive user data without proper authorization

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: Adding new endpoints, straightforward but not trivial
  - **Skills**: [`git-master`]
    - `git-master`: Need careful commits for new auth mechanism
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: No UI work, pure API development

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Task 2 (auth fixes need these endpoints)
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (existing code to follow):
  - `users/api.py:80-100` - Current `/me` endpoint pattern
  - `users/api.py:36-78` - Telegram auth controller structure

  **API References** (contracts to extend):
  - `users/schemas.py:14-21` - UserSchema for response format
  - `users/models.py` - UserProfile model structure

  **Security References** (auth patterns to consider):
  - Current JWT implementation for reference
  - Simple API key validation patterns

  **WHY Each Reference Matters**:
  - Existing `/me` endpoint shows response format to maintain
  - UserProfile model shows data structure available
  - Auth controller shows where to add simplified endpoints

  **Acceptance Criteria**:

  **Automated Verification**:
  ```bash
  # Agent runs:
  curl -s "http://localhost:8000/api/tg/users/me?telegram_id=12345" | jq '.username'
  # Assert: Returns username for authenticated user
  
  curl -s -X POST http://localhost:8000/api/tg/users/simple-auth \
    -H "Content-Type: application/json" \
    -d '{"telegram_id":12345}' | jq '.authorized'
  # Assert: Returns true for valid telegram_id
  ```

  **Evidence to Capture**:
  - [ ] New endpoint response verification
  - [ ] Simplified auth mechanism test
  - [ ] Backwards compatibility check with existing endpoints

  **Commit**: YES
  - Message: `feat(api): add simplified Telegram auth endpoints`
  - Files: `users/api.py`, possibly `users/schemas.py`
  - Pre-commit: `curl localhost:8000/api/tg/users/me?telegram_id=1`

- [ ] 5. Add Comprehensive Error Handling

  **What to do**:
  - Add try-catch blocks around all API calls in bot
  - Handle HTTP errors (401, 422, 500) with user-friendly messages
  - Add timeout handling for slow API responses
  - Log errors for debugging while showing clean messages to users
  - Add retry logic for temporary failures

  **Must NOT do**:
  - Hide all error details - some info helps users understand issues
  - Create infinite retry loops
  - Expose sensitive debugging info to Telegram users

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Adding error handling patterns, well-defined scope
  - **Skills**: [`git-master`]
    - `git-master`: Need organized commits for error handling
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: No UI work, pure error handling logic

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 2)
  - **Parallel Group**: Wave 2 (with Task 2)
  - **Blocks**: Task 3 (integration testing needs error handling)
  - **Blocked By**: Task 1 (need working response parsing first)

  **References**:

  **Pattern References** (existing code to improve):
  - `bot.py:49-62` - Current `fetch_data` and `post_request` methods
  - `bot.py:280-282` - Existing basic error handler

  **Error Handling Patterns** (libraries and techniques):
  - `httpx` library error types for HTTP exceptions
  - Python `asyncio.TimeoutError` for timeout handling
  - Telegram bot error message patterns

  **Logging References** (debugging setup):
  - `bot.py:37-38` - Current logger setup
  - Django logging configuration patterns

  **WHY Each Reference Matters**:
  - Current API methods show where error handling is needed
  - HTTP library docs show what exceptions to catch
  - Logging setup enables debugging of integration issues

  **Acceptance Criteria**:

  **Automated Verification**:
  ```bash
  # Agent runs:
  # Test with server down
  python -c "
  import asyncio
  import sys
  sys.path.append('.')
  from bot import BotHandlers
  
  async def test():
      handler = BotHandlers('http://localhost:9999')  # Wrong port
      result = await handler.fetch_data('/api/mentors/')
      print('Handles server down:', result is None)
      # Should not crash, should return None gracefully
  
  asyncio.run(test())
  "
  # Assert: Output shows graceful handling, no exceptions
  
  # Test with 404 endpoint
  curl -s http://localhost:8000/api/nonexistent | grep -q "404" && echo "404 handled"
  # Assert: Shows proper error handling
  ```

  **Evidence to Capture**:
  - [ ] Error condition test results
  - [ ] Graceful degradation verification
  - [ ] User-friendly error messages

  **Commit**: YES
  - Message: `feat(bot): add comprehensive error handling and retries`
  - Files: `bot.py`, possibly `run_bot.py`
  - Pre-commit: `python -c "from bot import BotHandlers; print('imports ok')"`

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `fix(bot): correct API response parsing for lists` | bot.py, run_bot.py | API format tests |
| 2 | `fix(bot): correct JWT token extraction from auth response` | bot.py, run_bot.py | Auth flow test |
| 3 | `test(bot): verify complete Telegram integration` | Test files | Full integration |
| 4 | `feat(api): add simplified Telegram auth endpoints` | users/api.py | Endpoint tests |
| 5 | `feat(bot): add comprehensive error handling and retries` | bot.py | Error condition tests |

---

## Success Criteria

### Verification Commands
```bash
python bot.py  # Expected: Bot starts without errors
curl localhost:8000/api/mentors/  # Expected: JSON array
curl localhost:8000/api/tg/users/me?telegram_id=1  # Expected: User data
```

### Final Checklist
- [ ] All bot commands work without crashes
- [ ] Authentication flow succeeds for protected operations
- [ ] API responses parse correctly in bot
- [ ] Error conditions handled gracefully
- [ ] No breaking changes to existing web API