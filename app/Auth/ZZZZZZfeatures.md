: utils.utils.py

hash_password
verify_password
create_access_token
create_refresh_token
decode_token
get_current_user
require_student
require_recruiter
oauth2_scheme

router.py

POST /auth/register/student
POST /auth/register/recruiter
POST /auth/login
POST /auth/refresh

schemas.py

StudentRegisterSchema
RecruiterRegisterSchema
LoginSchema
TokenSchema — returns access_token, refresh_token, token_type