# Transcript download failed

Date: 2026-10-13

Videos requested (playlist PLBcGPKNwWSiI7GzZu-QkjN3cDs2q0vJJK):
O_9JSq8c0tM, eOtv2O2iH0Q, bjEQXNLalwo, lApmNhYvE7k, Nuvhg2w39B8

YouTube could not be reached from the session environment: the outbound proxy
refused the CONNECT to www.youtube.com:443 (network policy denial). No transcripts
or metadata were retrieved, and nothing has been fabricated.

## youtube-transcript-api error (identical for all 5 IDs, shown for O_9JSq8c0tM)

```
ProxyError: HTTPSConnectionPool(host='www.youtube.com', port=443): Max retries exceeded with url: /watch?v=O_9JSq8c0tM (Caused by ProxyError('Unable to connect to proxy', OSError('Tunnel connection failed: 403 Forbidden')))
```

## yt-dlp error

```
ERROR: [youtube] O_9JSq8c0tM: Unable to download API page: ('Unable to connect to proxy', OSError('Tunnel connection failed: 403 Forbidden')) (caused by ProxyError("('Unable to connect to proxy', OSError('Tunnel connection failed: 403 Forbidden'))"))
```

## Proxy status

```
connect_rejected: gateway answered 403 to CONNECT (policy denial or upstream failure), host www.youtube.com:443
```
