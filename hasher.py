import hashlib

def hash(password : str):
    h = hashlib.sha256()
    h.update(password.encode())
    pass_hash = h.hexdigest()
    return pass_hash