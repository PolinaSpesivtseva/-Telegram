from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.sites.models import Site

class DefaultAccountAdapterCustom(DefaultAccountAdapter):
    #def get_login_redirect_url(self, request):
       # return "/"


    def clean_email(self, email):
        restricted_domain = "hse.ru"
        if email.split('@')[-1].lower() == restricted_domain:
            raise ValidationError("Регистрация с почтой @hse.ru запрещена.")
        return super().clean_email(email)

    def send_mail(self, template_prefix, email, context):
        site = Site.objects.get_current()
        ctx = {
            "email": email,
            "current_site": site,
        }
        ctx.update(context)

        # activation patch
        if "activate_url" in ctx.keys():
            ctx['activate_url'] = settings.URL_FRONT + \
                'accounts/verify-email/' + ctx['key']
        
        # password reset patch
        if "password_reset_url" in ctx.keys():
            ctx['password_reset_url'] = settings.URL_FRONT + \
                "/".join(ctx['password_reset_url'].split("/")[3:])

        msg = self.render_mail(template_prefix, email, ctx)
        msg.send()
