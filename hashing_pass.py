import bcrypt

async def hash_passwords(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt)


async def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password)