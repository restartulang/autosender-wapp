import keyring
import logging
import config

SERVICE = config.KEYRING_SERVICE

class CredentialNotFoundError(Exception):
    pass

def save_credentials(username: str, password: str) -> None:
    if not username or not password:
        raise ValueError("Username dan password tidak boleh kosong")
    keyring.set_password(SERVICE, 'username', username)
    keyring.set_password(SERVICE, 'password', password)
    logging.info(f'Credentials tersimpan untuk user: {username}')

def get_credentials() -> tuple[str, str]:
    username = keyring.get_password(SERVICE, 'username')
    password = keyring.get_password(SERVICE, 'password')
    if not username or not password:
        raise CredentialNotFoundError('Kredensial CMSS belum diatur')
    return username, password

def has_credentials() -> bool:
    try:
        get_credentials()
        return True
    except CredentialNotFoundError:
        return False
    except Exception as e:
        logging.error(f"Error checking credentials: {e}")
        return False

def clear_credentials() -> None:
    try:
        keyring.delete_password(SERVICE, 'username')
        keyring.delete_password(SERVICE, 'password')
    except Exception as e:
        logging.error(f"Error clearing credentials: {e}")
