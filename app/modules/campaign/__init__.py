"""Campaign module exports."""

from app.modules.campaign.model import Campaign
from app.modules.campaign.send_log import CampaignSendLog

__all__ = ["Campaign", "CampaignSendLog"]
