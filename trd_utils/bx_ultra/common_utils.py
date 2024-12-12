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
        payload_data = json.dumps(payload_data, separators=(',', ':'))

    if not trace_id:
        trace_id = uuid.uuid4().hex.replace("-", "")

    whole_parts = f"{first_part}{device_id}{platform_id}{app_version}{payload_data}"

    # do SHA256
    return hashlib.sha256(whole_parts.encode()).hexdigest().upper()


# my_data = '{"fundType":"1","marginCoinName":"USDT","marginType":"0","pageId":"0","pagingSize":"9999","quotationCoinId":"13"}'
my_data = {
    "marginCoinName": "USDT",
    "quotationCoinId": "13",
}
trace_id = "07eeea9de8cf4681b4b5a34867243d97"

ok = do_ultra_ss(
    e_param="95d65c73dc5c437",
    se_param="0ae9018fb7",
    le_param="f2eab69",
    timestamp=1734003279201,
    trace_id=trace_id,
    device_id="ff9d78b104a64f47a5d5b1c056389c75",
    platform_id="30",
    app_version="4.78.12",
    payload_data=my_data,
)

print(ok)


# 95d65c73dc5c4370ae9018fb7f2eab691730989174711 5d1b9fc1c79c4e2f82629c6128c2669d  f4a6e84f29464b048bc73f585b25248a304.77.19{}


# 95d65c73dc5c4370ae9018fb7f2eab69  1730989174711 58db86d42181485f98997bb5a949dd91  f4a6e84f29464b048bc73f585b25248a304.77.19{}


# locale=en; uuid=f4a6e84f29464b048bc73f585b25248a; theme=light; kline_time_zone=0; _ga=GA1.1.894882076.1724535655; _fbp=fb.1.1724535660838.817937290955837131; _ga_GH1NE7LJK0=GS1.1.1730062625.39.0.1730062625.0.0.0; _ga_F8FPFG5ZCL=GS1.1.1730062625.39.0.1730062625.0.0.0; cf_clearance=K.P6eYfJIHn60RBV0zQsaEIu9cg01lfZ4AMEQMiQcwI-1730320470-1.2.1.1-rUuDumQvMtsweO9AJ2ArdO90aV6kyxZnje3UxUUemJonh01l1ez87zcJQnQ3JIjQ_gVXsdEId5UtZKjk7o6gr7.2nBqZdLUqtfHGYWYyXtBM793Fh20rjJyFSYWHYcxR1AGHO3XO9EcJm4amVhVedhCL4Dn.8zqYNr2y16ml3m37uKhJPiqvpS8rysOYqro3LTM.rwV08XRC9Kn9Ka7cgfOnG3nQKcHzjwDjxxqzKX0Y5wD0VOtujy79z6HrF2uSOhEA1uMI_OouYBSxPI8A_2Gr_BAw20EXo4h4nS5wmbujpega0kIn6da5mKg6pcCjuqmQfL.e58h6HeF5MySjrkuNvkiBbjcmgE_BZ.7kRBJKut8fZbi.0zOsd0zUFQv8lC8iW3wIlwMskPLf_WCybwB3vrjnCQASmMRRQnJhHk5bpZyAdFGKTP6uVOvkAMKa; uid=1187333949809635334; user_token=eyJicyI6MCwiYWlkIjoxMDAwOSwicGlkIjoiMzAiLCJzaWQiOiI0MTE4OWQwMGQ3OGQxNDRjOGJlNjBiNjkwMGExMzc2MiIsImFsZyI6IkhTNTEyIn0.eyJzdWIiOiIxMTg3MzMzOTQ5ODA5NjM1MzM0IiwiZXhwIjoxNzMxMDM4NzY5LCJqdGkiOiJmNjY2ZGViYy1kZjQwLTRiNDctYTMzYy01MzY2OGNkZmZmYTkifQ.aDJxL5s0U3EwgwO_wvJZ9PL9DaHmrPPPeqHnhGY2vQ56lDoQllOwc-4BKICUsu_cCcdZ6yR4QqM1tsPPZyTmPg; muid=1187333949809635334; cf_bm=e6RDiSZu0dcu2vjrj70L_00koyRXXfvPHkPA0TDXHoU-1730985087-1.0.1.1-LFewW2CAFUFbJFVN0uwCWKETRPlKQpRhg0j5IL3POGdVmofx_iRIps4Aqh8ekSI9rF3XftDHW4rFVtdkLE6QEg; tokenExpiredAt=1731071491730; network_delay=504; lastCheckSessionAt=1730985274139


# cf_bm=VXdXpIKJOnACuA5x1_T.NqVDRajh7HH5uDogts6AQy4-1730985091-1.0.1.1-rzHh1aLEhwqbZgUwNwLCzMFmwpPaHC4NBGtag8.4HYZ9Og8JFUTAH3uHf_h_xLmvh3VpNIaE2IV4OI63WHIeOg; path=/; expires=Thu, 07-Nov-24 13:41:31 GMT; domain=.qq-os.com; HttpOnly; Secure; SameSite=None