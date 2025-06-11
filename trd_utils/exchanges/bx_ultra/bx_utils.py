import hashlib
import json
import uuid


default_e: str = (
    "\u0039\u0035\u0064\u0036\u0035\u0063\u0037\u0033\u0064\u0063\u0035"
    + "\u0063\u0034\u0033\u0037"
)
default_se: str = "\u0030\u0061\u0065\u0039\u0030\u0031\u0038\u0066\u0062\u0037"
default_le: str = "\u0066\u0032\u0065\u0061\u0062\u0036\u0039"

long_accept_header1: str = (
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
    + "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
)

def do_ultra_ss(
    e_param: str,
    se_param: str,
    le_param: str,
    timestamp: int,
    trace_id: str,
    device_id: str,
    platform_id: str,
    app_version: str,
    payload_data: str = None,
) -> str:
    if not e_param:
        e_param = default_e

    if not se_param:
        se_param = default_se

    if not le_param:
        le_param = default_le

    first_part = f"{e_param}{se_param}{le_param}{timestamp}{trace_id}"
    if not payload_data:
        payload_data = "{}"
    elif not isinstance(payload_data, str):
        # convert to json
        payload_data = json.dumps(payload_data, separators=(",", ":"), sort_keys=True)

    if not trace_id:
        trace_id = uuid.uuid4().hex.replace("-", "")

    whole_parts = f"{first_part}{device_id}{platform_id}{app_version}{payload_data}"

    # do SHA256
    return hashlib.sha256(whole_parts.encode()).hexdigest().upper()
