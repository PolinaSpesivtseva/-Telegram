from allauth.account.views import LoginView

class AlwaysRootLoginView(LoginView):
    """
    Всегда редиректит на /, игнорируя ?next=...
    """
    def get_success_url(self):
        # просто игнорируем всё и возвращаем корень
        return '/'
