from django.contrib.auth.backends import ModelBackend
from django.core.cache import cache
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Check if the IP is blocked
            ip_address = self.get_client_ip(request)
            if self.is_ip_blocked(ip_address):
                logger.warning(f'Blocked login attempt from IP: {ip_address}')
                return None

            # Get the user and validate
            user = self.get_user_model().objects.get(username=username)
            
            if not user.is_active:
                logger.warning(f'Login attempt for inactive user: {username}')
                return None

            if not user.check_password(password):
                self.handle_failed_login(user, ip_address)
                return None

            # Successful login
            user.reset_failed_login_attempts()
            user.last_login_ip = ip_address
            user.save(update_fields=['last_login_ip'])
            
            logger.info(f'Successful login for user: {username}')
            return user

        except self.get_user_model().DoesNotExist:
            # Use the same timing as a failed password check would take
            self.get_user_model().make_password('dummy')
            logger.warning(f'Login attempt for non-existent user: {username}')
            return None
        except Exception as e:
            logger.error(f'Authentication error: {str(e)}')
            return None

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

    def is_ip_blocked(self, ip_address):
        key = f'login_attempts_ip_{ip_address}'
        attempts = cache.get(key, 0)
        return attempts >= settings.MAX_LOGIN_ATTEMPTS_PER_IP

    def handle_failed_login(self, user, ip_address):
        # Increment failed login attempts for user
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
            user.lock_account()
        else:
            user.save(update_fields=['failed_login_attempts'])

        # Increment failed login attempts for IP
        key = f'login_attempts_ip_{ip_address}'
        attempts = cache.get(key, 0)
        cache.set(key, attempts + 1, settings.LOGIN_ATTEMPTS_TIMEOUT)

        logger.warning(f'Failed login attempt for user: {user.username} from IP: {ip_address}') 