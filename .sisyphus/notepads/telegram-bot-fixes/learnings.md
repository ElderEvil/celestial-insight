
## Telegram Auth Endpoint Pattern (2026-01-31)

### Implementation
Modified `/api/tg/users/me` endpoint to support dual authentication:
- **Telegram ID lookup**: `?telegram_id=X` query param (no JWT required)
- **JWT fallback**: Standard JWT auth for web clients

### Key Pattern
```python
@http_get("/me", response=UserSchema)
async def me(self, request, telegram_id: int | None = None):
    if telegram_id is not None:
        # Lookup via SocialAccount
        social_account = await sync_to_async(
            lambda: SocialAccount.objects.filter(provider="telegram", uid=str(telegram_id)).first()
        )()
        user = await sync_to_async(lambda: social_account.user)()
    else:
        # JWT auth fallback
        user = request.user
```

### Lessons
1. **HttpResponse bytes**: Django requires `HttpResponse(b"message")` not `HttpResponse("message")`
2. **LSP false positives**: Pyright doesn't understand Django's dynamic `objects` manager - runtime works fine
3. **Async wrapping**: All Django ORM calls need `sync_to_async()` wrapper in async views
4. **Removed AsyncJWTAuth**: Endpoint now handles auth logic internally instead of decorator

### Testing
- Django system check: ✅ passes
- Linting: ✅ passes (removed unused AsyncJWTAuth import)
- Bot can now call: `GET /api/tg/users/me?telegram_id=12345`

