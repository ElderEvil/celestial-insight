# OAuth Issues and Solutions

## Telegram "Bot domain invalid" Error

### Root Cause
Telegram OAuth validates the callback domain against the bot's domain whitelist. The domain `127.0.0.1:8000` is not whitelisted for the bot.

### Solution Steps (from Telegram Official Docs)

#### Step 1: Configure Bot Domain via @BotFather

1. Open Telegram and search for @BotFather
2. Send command: `/mybots`
3. Select your bot (Celestial Insight bot)
4. Send command: `/setdomain`
5. Enter domain: `127.0.0.1` (or your production domain)

**Important**: The bot's profile picture should match your website's logo, and the bot's name should reflect the connection. Users will see this bot when logging in.

#### Step 2: Verify Bot Configuration

Check bot settings:
- Bot username: @celestial_insight_bot (or your bot's username)
- Bot domain: Should match your application's domain
- Token: Should match TELEGRAM_BOT_SECRET in .env

#### Step 3: Test Telegram OAuth

After configuring the domain, test the OAuth flow:
```bash
curl -v http://127.0.0.1:8000/accounts/telegram/login/
```

Should redirect to: `https://oauth.telegram.org/auth?bot_id=...&domain=127.0.0.1:8000`

### Alternative: Use ngrok for Testing

If @BotFather doesn't allow localhost domains:
1. Install ngrok: `brew install ngrok` or `choco install ngrok`
2. Start tunnel: `ngrok http 8000`
3. Use ngrok URL for OAuth callbacks
4. Configure bot domain to match ngrok URL

### Telegram OAuth Flow (from official docs)

After successful authorization, Telegram returns:
- `id` - User ID
- `first_name` - User's first name
- `last_name` - User's last name
- `username` - Telegram username
- `photo_url` - Profile photo URL
- `auth_date` - Unix timestamp of authorization
- `hash` - HMAC-SHA256 signature for verification

The application must verify the hash using:
```
data_check_string = "auth_date=<auth_date>\nfirst_name=<first_name>\nid=<id>\nusername=<username>"
secret_key = SHA256(<bot_token>)
if hex(HMAC_SHA256(data_check_string, secret_key)) == hash:
    # data is from Telegram
```

## GitHub OAuth Callback Issues

### Configuration Check

Verify GitHub OAuth app settings:
1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Select your OAuth app
3. Verify callback URL: `http://127.0.0.1:8000/accounts/github/login/callback/`
4. Verify client ID matches settings

### Common Issues

1. **Callback URL mismatch**: Must match exactly (including trailing slash)
2. **Client secret expired**: Regenerate if needed
3. **App not authorized**: Check app permissions

## Google OAuth

### Configuration Status
- Settings are loaded correctly
- Google social account exists in database (from previous OAuth)
- Should work when user completes real OAuth flow

### Verification
```bash
curl -v http://127.0.0.1:8000/accounts/google/login/
```

Should redirect to Google OAuth with correct client_id and callback URL.