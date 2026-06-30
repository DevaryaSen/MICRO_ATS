Here's the full picture:

---

**Phase 1 — Core CRUD (do this now)**
```
Jobs         → create, get all, get one, delete, close
Applications → apply, get my apps, get applicants, move stage
Profiles     → get me, update me (student + recruiter)
```

---

**Phase 2 — Background Tasks (FastAPI built-in, no extra infra)**
```
Email triggers:
→ register         (welcome email)
→ forgot password  (OTP/reset link)
→ change password  (confirmation email)
→ stage update     (notify student their stage changed)
```

---

**Phase 3 — Image/File Uploads**
```
Cloudinary (free DAM) → profile pictures, resume, company logo
store only the URL in DB (already have those columns)
```

---

**Phase 4 — Redis**
```
Caching      → GET /jobs (heavy read, cache for 60s)
Rate limiting → POST /apply, POST /jobs (prevent spam)
Blocklist     → logout (blacklist JWT jti until expiry)
```

---

**Phase 5 — Deploy (EC2)**
```
Docker compose → FastAPI + Postgres + Redis
Nginx          → reverse proxy
EC2 t2.micro   → free tier, run for a week
```

---

**So finish in this order:**
```
1. Jobs CRUD
2. Applications CRUD  
3. Profiles CRUD
4. Background tasks (emails)
5. Cloudinary uploads
6. Redis (cache + rate limit + blocklist)
7. Deploy
```

Start with Jobs service?



alembic revision --autogenerate -m "add application model"
alembic upgrade head

uvivcorn run app.main:app -- reload


<!-- 
# @router.post("/refresh", response_model=TokenResponse)
# async def refresh_tokens(refresh_token: str, db: AsyncSession = Depends(get_db)):
#     payload = decode_token(refresh_token, expected_type="refresh")
    
#     # optionally: verify token exists in DB and hasn't been revoked
#     is_valid = await validate_stored_refresh_token(db, payload["sub"], refresh_token)
#     if not is_valid:
#         raise HTTPException(status_code=401, detail="Refresh token revoked or not found")

#     # rotate: issue new pair, invalidate old refresh token
#     await revoke_refresh_token(db, refresh_token)

#     access_token, access_expires = create_access_token(int(payload["sub"]), payload["role"])
#     new_refresh, refresh_expires = create_refresh_token(int(payload["sub"]), payload["role"])
#     await store_refresh_token(db, int(payload["sub"]), new_refresh, refresh_expires)

#     return TokenResponse(
#         access_token=access_token,
#         refresh_token=new_refresh,
#         role=payload["role"],
#         access_token_expires_at=access_expires,
#         refresh_token_expires_at=refresh_expires,
#     ) -->