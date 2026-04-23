# Auth0 SSO Setup Guide for Seed OI

This guide outlines how to configure Auth0 as the primary SSO broker for Seed OI, supporting Google login and preparing for enterprise connections like Microsoft Entra ID.

## 1. Auth0 Tenant Configuration

1. **Create an Auth0 Tenant**: Log in to the [Auth0 Dashboard](https://manage.auth0.com/).
2. **Create a Regular Web Application**:
   - Name: `Seed OI Web`
   - Allowed Callback URLs: `http://localhost:3000/login/callback`
   - Allowed Logout URLs: `http://localhost:3000`
   - Allowed Web Origins: `http://localhost:3000`
   - Grant Types: `Authorization Code`, `Refresh Token`, `PKCE`
   
> [!IMPORTANT]
> If you see a **"Callback URL mismatch"** error, ensure `http://localhost:3000/login/callback` is exactly matched in your Auth0 Application settings.

3. **API Identifier**:
   - Seed OI currently uses the **Auth0 Management API** identifier by default for simplified local setup.
   - Identifier: `https://dev-yiaflx7w15oc0yjq.us.auth0.com/api/v2/`

> [!IMPORTANT]
> If you see an **"Access Denied: Service not found"** error on the callback page, it means the `Identifier` in your `.env.local` doesn't match what Auth0 expects. Ensure `NEXT_PUBLIC_AUTH0_AUDIENCE` is exactly `https://dev-yiaflx7w15oc0yjq.us.auth0.com/api/v2/`.

## 2. Google Integration

1. Go to **Authentication > Social**.
2. Enable **Google / Gmail**.
3. (Optional) Provide your own Google Client ID and Secret for production use to avoid Auth0 dev keys.

## 3. Microsoft Entra ID (Future)

1. Go to **Authentication > Enterprise**.
2. Configure **Microsoft Azure AD**.
3. Map the connection to your `Seed OI Web` application.

## 4. Environment Variables

### Web App (`apps/web/.env.local`)
> [!TIP]
> **Restart your development server** (`./run_local.sh`) after creating or editing `.env.local` to ensure Next.js picks up the new variables.

```bash
NEXT_PUBLIC_AUTH0_DOMAIN=dev-yiaflx7w15oc0yjq.us.auth0.com
NEXT_PUBLIC_AUTH0_CLIENT_ID=yYnK6cMx1G5M2wCxQxi4FmETNzzZuTyC
NEXT_PUBLIC_AUTH0_AUDIENCE=https://dev-yiaflx7w15oc0yjq.us.auth0.com/api/v2/
```

### API Service (`apps/api-python/.env` or Config)
```bash
OIDC_ISSUER=https://dev-yiaflx7w15oc0yjq.us.auth0.com/
OIDC_AUDIENCE=https://dev-yiaflx7w15oc0yjq.us.auth0.com/api/v2/
PLATFORM_ADMINS=jake.osilla@seed-grow.com
```

## 5. Identity Mapping

Seed OI uses the `sub` claim from the Auth0 Access Token as the primary `external_id`.
On the first login, the `application/security/current_user.py` service:
1. Validates the token against Auth0 JWKS.
2. Checks if a user with the given `external_id` exists.
3. If not, checks by `email`.
4. If still not found, auto-provisions a new record in the internal `users` table, assigning roles based on the `PLATFORM_ADMINS` list.

## 6. Role Management

Internal roles are mapped as follows:
- **Admin**: Full access to all plants and settings.
- **PlantManager**: Full access to assigned plants.
- **Planner**: Access to risks and scenarios for assigned plants.
- **OperationsAnalyst**: Access to overview and risks for assigned plants.
- **Viewer**: Read-only access to assigned data.
