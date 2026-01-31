# Improve Telegram Bot UX with Mentor Selection

## TL;DR

> **Quick Summary**: Enhance Telegram bot user experience by removing /start from menu, adding mentor selection flow to reading creation, and fixing response parsing to show actual AI insights.
> 
> **Deliverables**: Improved bot UX with intuitive 3-step reading flow
> - Cleaned up main menu (remove /start button)
> - Mentor selection via inline keyboard before question input
> - Fixed reading responses to show actual celestial insights
> - Added fallback handlers for better navigation
> 
> **Estimated Effort**: Medium
> **Parallel Execution**: YES - 3 waves
> **Critical Path**: Menu fix → Mentor flow → Response parsing

---

## Context

### Original Request
User wants improved Telegram bot UX: remove /start from menu, add mentor selection before reading, fix reading responses, and make overall flow more intuitive.

### Interview Summary
**Key Discussions**:
- **Menu Layout**: Remove /start from persistent keyboard
- **Command Structure**: Separate Commands - keep /mentors for browsing, add mentor selection to /reading flow
- **Reading Flow**: Quick Flow (3 steps) - Mentor selection → Question input → Reading created
- **Test Strategy**: Manual testing in Telegram during development

**Research Findings**:
- **UX Best Practices**: Don't show onboarding commands in persistent menu, use inline keyboards for selections, provide step indicators
- **DX Patterns**: ConversationHandler with states, callback query patterns, persistence for state management
- **Current Issues**: Two bot implementations, hardcoded mentor_id=1, unused WAITING_FOR_MENTOR state, incomplete response parsing

### Metis Review
**Identified Gaps** (addressed):
- **Two Bot Files**: Only modify `bot.py` (standalone), ignore `run_bot.py` (management command)
- **Menu Replacement**: What replaces /start button - decided to reorganize 2x3 layout
- **Default Mentor**: For users without preferences - use first active mentor as fallback
- **Cancel Handler**: Add proper fallback for conversation exit
- **Active Mentor Validation**: Filter by is_active when building selection keyboard

---

## Work Objectives

### Core Objective
Improve Telegram bot UX by implementing mentor selection flow and fixing response display issues.

### Concrete Deliverables
- Updated main menu without /start button
- 3-step reading conversation: mentor → question → result
- Working mentor selection via inline keyboard
- Proper display of AI-generated insights
- Fallback handlers for conversation navigation

### Definition of Done
- [ ] `/start` command removed from keyboard menu
- [ ] `/reading` shows mentor selection as first step
- [ ] Reading responses show actual celestial insights
- [ ] Bot conversation includes cancel/back options
- [ ] All mentor selections work without crashes

### Must Have
- Clean menu layout without /start
- Mentor selection before question input
- Actual AI insight display (not fallback text)
- Proper error handling for all failure scenarios

### Must NOT Have (Guardrails)
- **No modifications to run_bot.py** - Only target bot.py standalone script
- **No API endpoint changes** - Use existing endpoints and response formats
- **No new persistent state** - Use session-only conversation state
- **No complex mentor management** - Simple selection, no editing/adding mentors
- **No breaking changes to existing commands** - Only enhance /reading flow

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO (only basic project structure)
- **User wants tests**: Manual-only
- **Framework**: Manual verification with bot commands in Telegram
- **QA approach**: Manual verification

### Manual Verification Only

Each TODO includes EXECUTABLE verification procedures that agents can run directly:

**For Bot Commands** (using interactive_bash for tmux):
```bash
# Agent executes via tmux session:
1. Start bot: python bot.py
2. Test commands via HTTP POST to simulate Telegram webhook
3. Verify expected responses and state transitions
```

**For API Integration** (using Bash curl):
```bash
# Agent runs:
curl -s "http://localhost:8000/api/mentors/?is_active=true" | jq '. | length'
# Assert: Returns number > 0 (active mentors exist)
```

**Evidence Requirements (Agent-Executable):**
- Bot startup logs without errors
- Menu keyboard structure verification
- Conversation state transition logs
- API response parsing validation

---

## Execution Strategy

### Parallel Execution Waves

```
Wave 1 (Start Immediately):
├── Task 1: Update main menu layout (no dependencies)
└── Task 4: Add mentor selection conversation state (no dependencies)

Wave 2 (After Wave 1):
├── Task 2: Implement mentor selection keyboard (depends: 4)
└── Task 5: Add fallback handlers (depends: 1)

Wave 3 (After Wave 2):
└── Task 3: Fix reading response parsing (depends: 2)

Critical Path: Task 1 → Task 4 → Task 2 → Task 3
Parallel Speedup: ~25% faster than sequential
```

### Dependency Matrix

| Task | Depends On | Blocks | Can Parallelize With |
|------|------------|--------|---------------------|
| 1 | None | 5 | 4 |
| 2 | 4 | 3 | None |
| 3 | 2 | None | None (final) |
| 4 | None | 2 | 1 |
| 5 | 1 | None | None |

### Agent Dispatch Summary

| Wave | Tasks | Recommended Agents |
|------|-------|-------------------|
| 1 | 1, 4 | delegate_task(category="quick", load_skills=["git-master"], run_in_background=true) |
| 2 | 2, 5 | dispatch parallel after Wave 1 completes |
| 3 | 3 | final integration task |

---

## TODOs

- [ ] 1. Update Main Menu Layout

  **What to do**:
  - Remove `/start` button from ReplyKeyboardMarkup in `bot.py:150-157`
  - Reorganize to 2x3 layout: `[/mentors, /me], [/cards, /reading], [/history, /help]`
  - Add `/help` button to provide access to command explanations
  - Keep `resize_keyboard=True` for mobile compatibility

  **Must NOT do**:
  - Remove /start command handler - only remove from keyboard
  - Change other keyboard layouts in card browsing flow
  - Touch run_bot.py management command version

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Simple keyboard layout change, clear pattern to follow
  - **Skills**: [`git-master`]
    - `git-master`: Need clean commit for UX change
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: No visual design work, pure layout adjustment

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 4)
  - **Blocks**: Task 5 (fallback handlers need new menu structure)
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (existing code to modify):
  - `bot.py:150-157` - Current keyboard layout with /start button
  - `bot.py:158` - reply_text call that uses this keyboard

  **UX References** (design guidance):
  - Research finding: "Don't show onboarding commands in persistent menu"
  - Telegram best practices: "/start automatically shown by Telegram apps on first interaction"

  **WHY Each Reference Matters**:
  - Current layout shows exactly what to change
  - UX research confirms this improvement aligns with best practices
  - Telegram's automatic /start handling means manual button is redundant

  **Acceptance Criteria**:

  **Manual Verification**:
  ```bash
  # Agent tests via bot simulation:
  python -c "
  import os
  os.environ['TELEGRAM_BOT_SECRET'] = 'test'
  os.environ['API_URL'] = 'http://localhost:8000'
  from bot import BotHandlers
  handler = BotHandlers('http://localhost:8000')
  
  # Simulate /help command to trigger menu display
  import asyncio
  from unittest.mock import MagicMock
  update = MagicMock()
  update.message.reply_text = MagicMock()
  
  # This would trigger menu display
  asyncio.run(handler.show_help(update, None))
  print('Menu verification: Check reply_text call for keyboard structure')
  "
  # Manual check: Verify keyboard layout doesn't contain '/start'
  ```

  **Evidence to Capture**:
  - [ ] New keyboard layout structure (code inspection)
  - [ ] Bot startup without errors
  - [ ] Help command shows proper menu structure

  **Commit**: YES
  - Message: `feat(bot): remove /start from main menu keyboard`
  - Files: `bot.py`
  - Pre-commit: `python -c "from bot import BotHandlers; print('imports ok')"`

- [ ] 2. Implement Mentor Selection Keyboard

  **What to do**:
  - Extend mentor selection display in WAITING_FOR_MENTOR state
  - Build inline keyboard from `/api/mentors/?is_active=true`
  - Follow pattern from `bot.py:249-276` (card suit selection)
  - Format: `🧙 {name} (Lvl {mystical_level})` with `callback_data="mentor_{slug}"`
  - Add "⬅ Back to Menu" button for navigation
  - Handle callback queries with pattern `mentor_*`

  **Must NOT do**:
  - Show inactive mentors (is_active=false)
  - Change existing callback patterns for cards
  - Add mentor editing/management features

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
    - Reason: Following existing pattern but extending functionality
  - **Skills**: [`git-master`]
    - `git-master`: Need organized commit for new feature
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: Using existing patterns, no design work needed

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 2 (sequential)
  - **Blocks**: Task 3 (response parsing needs mentor selection working)
  - **Blocked By**: Task 4 (needs conversation state defined)

  **References**:

  **Pattern References** (existing code to follow):
  - `bot.py:249-276` - Card suit inline keyboard pattern with callback_data
  - `bot.py:443-451` - CallbackQueryHandler registration pattern
  - `bot.py:268-276` - Callback handler method structure

  **API References** (data source and structure):
  - `mentors/api.py:14-22` - `/mentors/?is_active=true` endpoint
  - `mentors/schemas.py:7-15` - MentorSchema structure (id, name, slug, mystical_level, specialization)
  - `mentors/models.py:11-25` - Mentor model field definitions

  **State Management References**:
  - `bot.py:44-46` - Conversation state constants (WAITING_FOR_MENTOR already defined)
  - `bot.py:311-333` - Conversation entry point pattern

  **WHY Each Reference Matters**:
  - Existing card pattern shows exact keyboard construction approach
  - Mentor API defines data structure and filtering requirements
  - State management shows how to integrate with ConversationHandler

  **Acceptance Criteria**:

  **Manual Verification**:
  ```bash
  # Agent verifies mentor data available:
  curl -s "http://localhost:8000/api/mentors/?is_active=true" | jq '. | map(select(.is_active)) | length'
  # Assert: Returns count > 0
  
  # Test keyboard structure:
  python -c "
  import asyncio
  import sys
  sys.path.append('.')
  from bot import BotHandlers
  
  async def test():
      handler = BotHandlers('http://localhost:8000')
      mentors = await handler.fetch_data('/api/mentors/?is_active=true')
      print('Mentors fetched:', len(mentors) if mentors else 0)
      print('First mentor structure:', mentors[0].keys() if mentors else 'None')
  
  asyncio.run(test())
  "
  # Assert: Shows mentor data fetched successfully
  ```

  **Evidence to Capture**:
  - [ ] Mentor API data retrieval verification
  - [ ] Inline keyboard button construction
  - [ ] Callback handler registration

  **Commit**: YES
  - Message: `feat(bot): add mentor selection inline keyboard to reading flow`
  - Files: `bot.py`
  - Pre-commit: `curl localhost:8000/api/mentors/?is_active=true | jq length`

- [ ] 3. Fix Reading Response Parsing

  **What to do**:
  - Update response parsing in `handle_reading_question` to show actual `celestial_insight`
  - Replace fallback "The cards have spoken" with proper AI insight
  - Handle both success (dict with celestial_insight) and error (string) responses
  - Ensure insight generation call works properly (`/readings/{id}/insight` endpoint)
  - Add loading indicator while insight is being generated

  **Must NOT do**:
  - Change API response format - only fix client parsing
  - Skip insight generation step - both create + insight required for complete reading

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Response parsing fix, clear bug to resolve
  - **Skills**: [`git-master`]
    - `git-master`: Need careful commit of response parsing logic
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: No UI work, pure data handling logic

  **Parallelization**:
  - **Can Run In Parallel**: NO
  - **Parallel Group**: Wave 3 (final verification)
  - **Blocks**: None (final task)
  - **Blocked By**: Task 2 (needs mentor selection working)

  **References**:

  **Pattern References** (existing code to fix):
  - `bot.py:356-368` - Current response parsing logic with fallback
  - `bot.py:359-372` - Insight generation API call pattern

  **API References** (response structure to handle):
  - `tarot/schemas.py:45-47` - ReadingSchema with celestial_insight field
  - `tarot/services/reading_service.py:34-100` - Returns Union[Reading, str]

  **Error Handling References** (patterns to follow):
  - `bot.py:364-375` - Existing HTTP status code handling
  - `tarot/services/reading_service.py:67-91` - Error message formats

  **WHY Each Reference Matters**:
  - Current parsing shows exact logic to fix
  - ReadingSchema defines structure containing actual insight
  - Service layer shows when strings vs objects are returned

  **Acceptance Criteria**:

  **Manual Verification**:
  ```bash
  # Agent creates test reading and verifies insight:
  TOKEN=$(curl -s -X POST "http://localhost:8000/api/tg/users/auth" \
    -H "Content-Type: application/json" \
    -d '{"telegram_id": 12345, "username": "testuser"}' | jq -r '.access')
  
  # Create reading
  READING=$(curl -s -X POST "http://localhost:8000/api/tg/tarot/readings?question=Should I change careers?&mentor_id=1" \
    -H "Authorization: Bearer $TOKEN")
  READING_ID=$(echo $READING | jq -r '.id')
  
  # Generate insight
  INSIGHT=$(curl -s -X POST "http://localhost:8000/api/tg/tarot/readings/$READING_ID/insight" \
    -H "Authorization: Bearer $TOKEN")
  CELESTIAL=$(echo $INSIGHT | jq -r '.celestial_insight')
  
  # Verify non-empty insight
  echo "Insight length: ${#CELESTIAL}"
  # Assert: Length > 50 (substantial insight, not fallback)
  ```

  **Evidence to Capture**:
  - [ ] Successful reading creation with insight
  - [ ] Non-fallback celestial insight text
  - [ ] Proper error message handling

  **Commit**: YES
  - Message: `fix(bot): display actual celestial insights in reading responses`
  - Files: `bot.py`
  - Pre-commit: `python -c "from bot import BotHandlers; print('imports ok')"`

- [ ] 4. Add Mentor Selection Conversation State

  **What to do**:
  - Add WAITING_FOR_MENTOR as first state in /reading ConversationHandler
  - Modify `create_reading` to show mentor selection instead of jumping to question
  - Store selected mentor_id in `context.user_data["selected_mentor_id"]`
  - Add CallbackQueryHandler for `mentor_*` pattern to process mentor selection
  - Update state transitions: mentor selection → question input → completion

  **Must NOT do**:
  - Change existing WAITING_FOR_QUESTION state logic
  - Add new conversation handlers - extend existing one
  - Modify mentor API - use existing endpoints

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Adding state to existing ConversationHandler, clear pattern
  - **Skills**: [`git-master`]
    - `git-master`: Need structured commit for conversation flow
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: Following existing conversation patterns

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Task 1)
  - **Blocks**: Task 2 (keyboard needs state defined)
  - **Blocked By**: None (can start immediately)

  **References**:

  **Pattern References** (existing code to extend):
  - `bot.py:44-46` - Conversation state constants (WAITING_FOR_MENTOR already exists)
  - `bot.py:468-475` - ConversationHandler setup with states
  - `bot.py:311-333` - Entry point pattern for conversations

  **State Management References**:
  - `bot.py:325` - `context.user_data["access_token"]` storage pattern
  - Conversation best practice: Store `context.user_data["selected_mentor_id"]`

  **API Integration References**:
  - `bot.py:352` - Current hardcoded mentor_id=1 to replace
  - `mentors/api.py:14-22` - Mentor list endpoint to integrate

  **WHY Each Reference Matters**:
  - Existing conversation setup shows exact structure to extend
  - Storage patterns show how to persist mentor selection
  - API endpoints provide mentor data for selection

  **Acceptance Criteria**:

  **Manual Verification**:
  ```bash
  # Agent verifies conversation state setup:
  python -c "
  import sys
  sys.path.append('.')
  from bot import WAITING_FOR_MENTOR, WAITING_FOR_QUESTION
  print('States defined:', WAITING_FOR_MENTOR, WAITING_FOR_QUESTION)
  print('WAITING_FOR_MENTOR should be 1')
  print('WAITING_FOR_QUESTION should be 2')
  "
  # Assert: States properly defined in sequence
  ```

  **Evidence to Capture**:
  - [ ] Conversation states properly defined
  - [ ] ConversationHandler includes mentor selection state
  - [ ] State transition logic implemented

  **Commit**: YES
  - Message: `feat(bot): add mentor selection state to reading conversation`
  - Files: `bot.py`
  - Pre-commit: `python -c "from bot import WAITING_FOR_MENTOR; print('state ok')"`

- [ ] 5. Add Fallback Handlers for Navigation

  **What to do**:
  - Add `/cancel` command to ConversationHandler fallbacks
  - Add proper conversation termination with menu restoration
  - Handle unexpected input during mentor selection (non-callback text)
  - Add timeout handling for abandoned conversations
  - Provide "⬅ Back" options in conversation states

  **Must NOT do**:
  - Add complex navigation - keep simple cancel/back only
  - Change existing error handling patterns
  - Add new global handlers outside conversation

  **Recommended Agent Profile**:
  - **Category**: `quick`
    - Reason: Adding standard fallback handlers, well-defined pattern
  - **Skills**: [`git-master`]
    - `git-master`: Need organized commit for navigation improvements
  - **Skills Evaluated but Omitted**:
    - `frontend-ui-ux`: No design work, pure conversation logic

  **Parallelization**:
  - **Can Run In Parallel**: YES (with Task 2)
  - **Parallel Group**: Wave 2 (with Task 2)
  - **Blocks**: None
  - **Blocked By**: Task 1 (needs menu structure defined)

  **References**:

  **Pattern References** (conversation patterns to follow):
  - Research: ConversationHandler best practice - always provide cancel/fallback
  - `telegram.ext.ConversationHandler` - fallbacks parameter usage

  **Error Handling References**:
  - `bot.py:395` - Current error handler pattern
  - `bot.py:158` - Menu restoration pattern after operations

  **WHY Each Reference Matters**:
  - Research shows fallbacks are essential for good UX
  - Existing patterns show how to restore normal bot state
  - Error handler provides template for unexpected input handling

  **Acceptance Criteria**:

  **Manual Verification**:
  ```bash
  # Agent verifies fallback handlers:
  python -c "
  import sys
  sys.path.append('.')
  from bot import main
  print('Bot configuration includes fallback handlers')
  # Check that ConversationHandler has non-empty fallbacks list
  "
  # Manual test: /cancel during conversation should work
  ```

  **Evidence to Capture**:
  - [ ] Fallback handlers properly registered
  - [ ] Cancel command terminates conversation gracefully
  - [ ] Unexpected input handled properly

  **Commit**: YES
  - Message: `feat(bot): add fallback handlers and navigation to reading flow`
  - Files: `bot.py`
  - Pre-commit: `python -c "from bot import BotHandlers; print('handlers ok')"`

---

## Commit Strategy

| After Task | Message | Files | Verification |
|------------|---------|-------|--------------|
| 1 | `feat(bot): remove /start from main menu keyboard` | bot.py | Menu structure |
| 2 | `feat(bot): add mentor selection inline keyboard to reading flow` | bot.py | Mentor selection |
| 3 | `fix(bot): display actual celestial insights in reading responses` | bot.py | Response parsing |
| 4 | `feat(bot): add mentor selection state to reading conversation` | bot.py | State setup |
| 5 | `feat(bot): add fallback handlers and navigation to reading flow` | bot.py | Navigation |

---

## Success Criteria

### Verification Commands
```bash
python bot.py  # Expected: Bot starts without errors
curl localhost:8000/api/mentors/?is_active=true  # Expected: Array of active mentors
```

### Final User Flow
1. User types `/reading`
2. Bot shows: "🔮 Choose your mystical guide:" + mentor buttons
3. User taps mentor → Bot: "✨ You've chosen [Mentor]! What guidance do you seek?"
4. User sends question → Bot creates reading + shows actual AI insight

### Final Checklist
- [ ] Main menu excludes /start button
- [ ] `/reading` starts with mentor selection
- [ ] Mentor selection shows active mentors with levels
- [ ] Reading responses display actual celestial insights
- [ ] Cancel/back navigation works throughout flow