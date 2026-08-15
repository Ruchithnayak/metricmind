# Security Notes

The offline NOVA demo uses development credentials and is not an authentication system for production use.

Before production deployment:
- Move credentials to a secure identity provider.
- Store secrets outside source control.
- Add role-based permissions.
- Add server-side authorization for sensitive actions.
- Encrypt sensitive data at rest and in transit.
