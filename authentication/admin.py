from django.contrib import admin
from .models import MoneyTransfer,AccountProfile,LoginPins,BanUser,ImfBan


admin.site.register(MoneyTransfer)
admin.site.register(AccountProfile)
admin.site.register(LoginPins)
admin.site.register(BanUser)
admin.site.register(ImfBan)


