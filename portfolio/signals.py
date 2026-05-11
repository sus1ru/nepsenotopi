from django.db.models.signals import post_delete
from django.dispatch import receiver

from portfolio.models import PortfolioShare


@receiver(post_delete, sender=PortfolioShare)
def recalculate_wacc_on_portfolio_share_delete(sender, instance, **kwargs):
    PortfolioShare.recalculate_waccs(instance.user_id, instance.security_id)
