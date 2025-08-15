# bot/utils/api_client.py

import aiohttp
import logging
from bot.config import DJANGO_API_URL

logger = logging.getLogger(__name__)


class DjangoAPIClient:
    def __init__(self):
        self.base_url = DJANGO_API_URL

    async def add_channel(self, owner_id, channel_id, title, username, category):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}add-channel/",
                    json={
                        "owner_id": owner_id,
                        "channel_id": channel_id,
                        "title": title,
                        "username": username,
                        "category": category
                    }
                ) as response:
                    if response.status in [200, 201]:
                        return await response.json()
                    else:
                        text = await response.text()
                        logger.error(f"Add channel error: {response.status} - {text}")
                        raise Exception(f"HTTP {response.status}")
        except Exception as e:
            logger.error(f"Add channel exception: {e}")
            raise

    async def get_subscription_task(self, user_id):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}get-task/",
                    json={"user_id": user_id}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        text = await response.text()
                        logger.error(f"Get task error: {response.status} - {text}")
                        return {"message": "No channels available"}
        except Exception as e:
            logger.error(f"Get task exception: {e}")
            return {"message": "Error getting task"}

    async def confirm_subscription(self, user_id, task_id):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}confirm-subscription/",
                    json={
                        "user_id": user_id,
                        "task_id": task_id
                    }
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        text = await response.text()
                        logger.error(f"Confirm subscription error: {response.status} - {text}")
                        raise Exception(f"HTTP {response.status}")
        except Exception as e:
            logger.error(f"Confirm subscription exception: {e}")
            raise