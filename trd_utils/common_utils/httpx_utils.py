
import json
import httpx


def httpx_resp_to_json(
    response: httpx.Response,
    parse_float=None,
) -> dict:
    try:
        return response.json(parse_float=parse_float)
    except UnicodeDecodeError:
        # try to decompress manually
        import gzip
        import brotli

        content_encoding = str(response.headers.get("Content-Encoding", "")).lower()
        content = response.content

        if "gzip" in content_encoding:
            content = gzip.decompress(content)
        elif "br" in content_encoding:
            content = brotli.decompress(content)
        elif "deflate" in content_encoding:
            import zlib

            content = zlib.decompress(content, -zlib.MAX_WBITS)
        else:
            raise ValueError(
                f"failed to detect content encoding: {content_encoding}"
            )

        # Now parse the decompressed content
        return json.loads(content.decode("utf-8"), parse_float=parse_float)

