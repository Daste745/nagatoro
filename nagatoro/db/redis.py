import logging

from redis import Redis

from nagatoro.objects import Config


log = logging.getLogger(__name__)


def init_redis(config: Config, db: int = 0) -> Redis:
    log.info(
        f"Initializing Redis connection to db #{db} on "
        f"{config.redis_url}:{config.redis_port}."
    )

    connection = Redis(
        host=config.redis_url,
        port=config.redis_port,
        db=db,
        username=config.redis_user,
        password=config.redis_passwd,
    )

    log.info(f"Successfully connected to Redis db #{db}.")
    return connection
