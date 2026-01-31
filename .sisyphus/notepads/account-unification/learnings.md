# Learnings: Account Unification

## Task 3: Auto-Merge on Web Signup

### Implementation Pattern
- **Custom Allauth Adapter**: Created `users/adapters.py` with `AccountAdapter` extending `DefaultAccountAdapter`
- **Hook Method**: Override `pre_social_login` to intercept social login before account creation
- **Merge Logic**: Check for existing user by email, verify Telegram account exists, then link new social account

### Key Allauth Patterns
1. **`pre_social_login` hook**: Called before social login is processed, perfect for custom merge logic
2. **`sociallogin.is_existing`**: Check if social account is already connected (skip merge if true)
3. **`sociallogin.connect(request, user)`**: Link new social account to existing user (the merge operation)

### Configuration
- **Setting**: `ACCOUNT_ADAPTER = "users.adapters.AccountAdapter"` in settings.py
- **Location**: Add after `EMAIL_BACKEND` and before `ACCOUNT_AUTHENTICATION_METHOD`

### Edge Cases Handled
1. **No email in social login**: Skip merge (some providers don't provide email)
2. **Already connected**: Skip merge (social account already linked)
3. **No existing user**: Skip merge (no account to merge with)
4. **Multiple users with same email**: Use first user (shouldn't happen with proper constraints)
5. **No Telegram account**: Skip merge (only merge if Telegram user exists)

### Security Considerations
- **Email verification**: Currently disabled (`ACCOUNT_EMAIL_VERIFICATION = "none"`)
- **Token preservation**: Handled automatically by linking to existing user (UserProfile remains intact)
- **Account ownership**: Primary account = first created (Telegram if exists)

### Testing Approach
- **Manual verification**: Django system check passes
- **Lint verification**: Ruff check passes
- **Integration testing**: Deferred to Task 5 (full flow testing)

### Code Quality
- **Logging**: Added info/debug logging for merge operations
- **Error handling**: Try/except for User.DoesNotExist and MultipleObjectsReturned
- **Type safety**: Used `get_user_model()` for User model reference
- **Documentation**: Module and method docstrings explain merge logic

### Related Files
- `users/adapters.py`: New file with custom adapter
- `celestial_insight/settings.py`: Added ACCOUNT_ADAPTER setting
- `users/api.py`: Existing patterns for SocialAccount creation
- `users/models.py`: UserProfile structure (tokens preserved)
