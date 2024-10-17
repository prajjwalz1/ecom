from django.db.models.signals import post_save,pre_delete
from django.dispatch import receiver
from .models import Product
import requests
#loggingsetup
import logging
logger = logging.getLogger('app')

# to load the environment variables
import os
from dotenv import load_dotenv
load_dotenv()

import os
import logging
import asyncio
import aiohttp
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Product

logger = logging.getLogger('product')

async def clear_cache(instance_id):
    base_url = os.environ.get("NEXT_BASE_URL")
    next_url_to_clear_cache = f"{base_url}/api/delete"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(next_url_to_clear_cache, timeout=5) as response:
                if response.status == 200:
                    logger.info(f"Cache cleared successfully for Product {instance_id} at URL: {next_url_to_clear_cache}")
                else:
                    logger.error(f"Failed to clear cache for Product {instance_id}. Status Code: {response.status}")
    except Exception as e:
        logger.exception(f"Exception occurred while clearing cache for Product {instance_id}: {e}")

async def clear_specific_product_cache(instance_id):
    # https://infotech-frontend.pages.dev/api/cache-product/instance_id
    base_url = os.environ.get("NEXT_BASE_URL")
    next_url_to_clear_cache = f"{base_url}/api/cache-product/{instance_id}"
    print(next_url_to_clear_cache)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(next_url_to_clear_cache, timeout=5) as response:
                if response.status == 200:
                    logger.info(f"Cache cleared successfully for Product {instance_id} at URL: {next_url_to_clear_cache}")
                else:
                    logger.error(f"Failed to clear cache for Product {instance_id}. Status Code: {response.status}")
    except Exception as e:
        logger.exception(f"Exception occurred while clearing cache for Product {instance_id}: {e}")

@receiver(post_save, sender=Product)
def clear_cache_next_server(sender, instance, created, **kwargs):
    logger.debug(f"Created Product: {instance.id}")
    asyncio.run(clear_cache(instance.id))

@receiver(post_save, sender=Product)
def clear_cache_specific_product_server(sender, instance, created, **kwargs):
    if not created:
        print("...............................................",instance.id)
        logger.debug(f"updated Product.................................................: {instance.id}")
        asyncio.run(clear_specific_product_cache(instance.id))

@receiver(pre_delete, sender=Product)
def clear_cache_on_delete(sender, instance, **kwargs):
    logger.debug(f"Deleting Product: {instance.id}")
    asyncio.run(clear_cache(instance.id))
