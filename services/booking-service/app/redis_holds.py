"""
Temporary ticket reservation ("hold") logic backed by Redis.

Why this is safe under concurrency:
  Redis executes each EVAL of a Lua script atomically and single-threadedly.
  The reserve script therefore performs "read currently-held quantity,
  compare against available capacity, write the new hold" as one
  indivisible step -- two concurrent requests for the last remaining
  ticket cannot both observe capacity as free.

Data model per ticket type `tt`:
  hold:{tt}:{reservation_id}   -> quantity held (string), TTL = reservation TTL
  holds_index:{tt}             -> Redis SET of reservation_ids that (may) hold this type

`holds_index` entries are lazily pruned: whenever we sum active holds we
check EXISTS for each member and drop stale ones. This tolerates keys
expiring in Redis without a separate expiry callback/consumer.
"""
from __future__ import annotations

import redis

from .config import settings

_RESERVE_SCRIPT = """
local tt_key = KEYS[1]
local index_key = KEYS[2]
local hold_key = KEYS[3]
local reservation_id = ARGV[1]
local requested_qty = tonumber(ARGV[2])
local available_capacity = tonumber(ARGV[3])
local ttl_seconds = tonumber(ARGV[4])

local members = redis.call('SMEMBERS', index_key)
local held = 0
for _, member in ipairs(members) do
    local key = tt_key .. ':' .. member
    local qty = redis.call('GET', key)
    if qty then
        held = held + tonumber(qty)
    else
        redis.call('SREM', index_key, member)
    end
end

if held + requested_qty > available_capacity then
    return {0, held}
end

redis.call('SET', hold_key, requested_qty, 'EX', ttl_seconds)
redis.call('SADD', index_key, reservation_id)
redis.call('EXPIRE', index_key, ttl_seconds * 4)
return {1, held}
"""

_RELEASE_SCRIPT = """
local index_key = KEYS[1]
local hold_key = KEYS[2]
local reservation_id = ARGV[1]
redis.call('DEL', hold_key)
redis.call('SREM', index_key, reservation_id)
return 1
"""


class TicketHoldStore:
    def __init__(self) -> None:
        self._client = redis.from_url(settings.redis_url, decode_responses=True)
        self._reserve = self._client.register_script(_RESERVE_SCRIPT)
        self._release = self._client.register_script(_RELEASE_SCRIPT)

    def held_quantity(self, ticket_type_id: str) -> int:
        index_key = f"holds_index:{ticket_type_id}"
        members = self._client.smembers(index_key)
        total = 0
        for member in members:
            qty = self._client.get(f"hold:{ticket_type_id}:{member}")
            if qty is None:
                self._client.srem(index_key, member)
            else:
                total += int(qty)
        return total

    def try_reserve(self, ticket_type_id: str, reservation_id: str, quantity: int, available_capacity: int) -> tuple[bool, int]:
        tt_key = f"hold:{ticket_type_id}"
        index_key = f"holds_index:{ticket_type_id}"
        hold_key = f"hold:{ticket_type_id}:{reservation_id}"
        result = self._reserve(
            keys=[tt_key, index_key, hold_key],
            args=[reservation_id, quantity, available_capacity, settings.reservation_ttl_seconds],
        )
        success, held = int(result[0]), int(result[1])
        return bool(success), held

    def release(self, ticket_type_id: str, reservation_id: str) -> None:
        index_key = f"holds_index:{ticket_type_id}"
        hold_key = f"hold:{ticket_type_id}:{reservation_id}"
        self._release(keys=[index_key, hold_key], args=[reservation_id])

    def is_active(self, ticket_type_id: str, reservation_id: str) -> bool:
        return self._client.exists(f"hold:{ticket_type_id}:{reservation_id}") == 1


ticket_hold_store = TicketHoldStore()
