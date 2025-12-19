# Security Policy

## Supported Versions

We actively support the latest released version of ytmusicapi.

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |
| < Latest | :x:               |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

### Do NOT:
- Open a public GitHub issue
- Disclose the vulnerability publicly before it's been addressed

### Do:
1. Email security details to: ytmusicapi@gmail.com
2. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect:
- **Initial Response**: Within 48 hours
- **Status Updates**: Every 5-7 days
- **Resolution Timeline**: We aim to address critical issues within 30 days

### After Resolution:
- You'll be credited in the security advisory (unless you prefer to remain anonymous)
- A security advisory will be published on GitHub
- A patch release will be issued

## Security Best Practices

When using ytmusicapi:

1. **Credentials**: Never commit authentication tokens or credentials to version control
2. **Dependencies**: Keep ytmusicapi and its dependencies up to date
3. **Input Validation**: Validate user inputs before passing to ytmusicapi functions
4. **Rate Limiting**: Implement appropriate rate limiting to avoid service abuse
5. **Error Handling**: Don't expose detailed error messages to end users

## Known Security Considerations

- Authentication tokens should be stored securely (encrypted at rest)
- OAuth tokens have expiration times and should be refreshed appropriately
- API requests go through YouTube Music servers - treat your credentials as you would your Google account password

Thank you for helping keep ytmusicapi and its users safe!
