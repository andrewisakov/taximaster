from .config import AUTH_KEY
import gino
import aiopg

def users_list() -> list:
    SELECT = (
        'select u.id, u.tm_password '
        'from access_user u '
        'left join radio_admins ra on (ra.user_id = u.id) '
        'where (coalesce(u.deleted, 0) = 0) '
        'and (coalesce(u.is_service, 0) = 0) '
        'and (u.tm_password is not null) '
        'and (coalesce(u.dismissed, 0) = 0) '
        'order by is_admin, u.name'
    )

def unhash_password(hash_pwd: str) -> str:
    """ Convert hash string in password """
    if not isinstance(hash_pwd, (str, )):
        return

    digits = [int(''.join(z), 16) for z in list(zip(hash_pwd[0::2], hash_pwd[1::2]))]
    return ''.join([chr(ord(AUTH_KEY[i]) ^ d) for i, d in enumerate(digits)])
        

def hash_password(password: str) -> str:
    """ Convert password in hash string """
    if not isinstance(password, (str, )):
        return 
    
    return ''.join([str(hex(ord(p.encode('cp1251')) ^ ord(AUTH_KEY[i].encode('cp1251'))))[2:].zfill(2) for i, p in enumerate(password[:15])])


async def authenticate(user_name: str, password: str, db: aiopg.pool) -> bool:
    async with db.acquire() as con:
        async with con.cursor() as c:
            await c.execute(
                ('select u.id, u.tm_password, u.name, coalesce(ra.user_id, 1, 0) as is_admin '
                 'from access_users u '
                 'join radio_admins ra on (ra.user_id=u.id) '
                 'where (coalesce(u.deleted, 0) = 0) '
                 'and (coalesce(u.is_service, 0) = 0) '
                 'and (u.tm_password is not null) '
                 'and (coalesce(u.dismissed, 0) = 0) '
                 'and u.name = %(user_name)s '
                 'and u.password = %(password)s '
                 'order by is_admin, u.name;'
                 ),
                 {'user_name': user_name, 'password': hash_password(password)}
            )
            r = await c.fetchone()
            if r:
                r = {cn.name :r[ix] for ix, cn in enumerate(c.description)}
            return r
