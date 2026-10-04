# Network sweep while the Raspberry Pi was offline

The user disconnected the complete Raspberry Pi, not merely the USB camera.
The initial offline sweep began at 2026-09-26T19:49:01Z
(2026-09-26T21:49:01+0200). A stronger follow-up used five ARP retries across
the complete `10.0.0.0/24` network and five IPv6 all-nodes multicast probes.

## Stable IPv4/MAC responders

| IPv4 | MAC | Reported vendor |
|---|---|---|
| 10.0.0.1 | 9c:a2:f4:6c:f1:36 | TP-Link Corporation Limited |
| 10.0.0.2 | d0:14:11:90:53:b2 | Airthings |
| 10.0.0.4 | c8:2e:18:f9:ae:f4 | Unknown |
| 10.0.0.6 | 8c:86:1e:64:1b:93 | Apple, Inc. |
| 10.0.0.7 | 10:20:ba:43:a6:24 | Unknown |
| 10.0.0.9 | 34:90:ea:c6:80:86 | Unknown |
| 10.0.0.10 | 98:ec:65:06:2e:6f | Cosesy ApS |
| 10.0.0.17 | f8:71:a6:b7:aa:f4 | Unknown |
| 10.0.0.21 | 68:63:59:db:18:e4 | Advanced Digital Broadcast SA |
| 10.0.0.32 | 78:45:58:e5:5b:58 | Ubiquiti Networks Inc. |
| 10.0.0.33 | 44:09:da:1a:ad:7f | Unknown |
| 10.0.0.43 | 94:dd:f8:28:ee:7c | Brother Industries, LTD. |
| 10.0.0.45 | 1c:69:7a:4c:50:37 | EliteGroup Computer Systems Co., LTD |
| 10.0.0.50 | c6:82:18:24:5f:2c | Locally administered |
| 10.0.0.53 | 34:2f:bd:e3:61:e3 | Nintendo Co., Ltd. |
| 10.0.0.59 | 30:05:5c:4d:8c:a5 | Brother Industries, LTD. |
| 10.0.0.63 | d4:f3:2d:fb:de:61 | Unknown |
| 10.0.0.74 | a8:3f:a1:7c:95:a5 | Plejd AB |
| 10.0.0.80 | 9c:75:6e:39:b8:7c | Ajax Systems DMCC |
| 10.0.0.85 | 9c:75:6e:39:b8:7d | Ajax Systems DMCC |
| 10.0.0.93 | 30:56:0f:5e:d0:fc | Unknown; known host `agogo` |
| 10.0.0.95 | ca:68:03:29:97:8a | Locally administered; confirmed `Gourd.local` |
| 10.0.0.109 | d4:ce:40:38:5b:59 | Unknown |
| 10.0.0.123 | 90:09:d0:a0:bb:a2 | Synology Incorporated |
| 10.0.0.138 | f4:4d:5c:57:28:d0 | Zyxel Communications Corporation |

The first offline sweep missed `10.0.0.50`, but a direct three-retry ARP probe
and the five-retry full sweep both proved that it remained online. It is
therefore not the disconnected Pi.

## IPv6 all-nodes responders

The robust offline probe observed these remote link-local addresses:

- `fe80::3035:f174:ca61:3faa%en0`
- `fe80::3256:fff:fe5:d0fc%en0`
- `fe80::f64d:5cff:fe57:28d0%en0`
- `fe80::7a45:58ff:fee5:5b58%en0`
- `fe80::aa3f:a1ff:fe7c:95a5%en0`
- `fe80::1c7d:374b:1ecc:e1a8%en0`
- `fe80::96dd:f8ff:fe28:ee7c%en0`
- `fe80::a4:1719:e433:83c0%en0`
- `fe80::14ea:f6e1:52b6:143a%en0`

## Interpretation

No device from the original one-pass connected-state ARP list was reliably
absent in the offline state. The connected snapshot was too shallow for a
definitive negative comparison: several ordinary LAN devices responded only in
the later, stronger sweep. The next discriminating test is a positive one:
power the Pi back on, run the same five-retry sweep, and identify the new
IPv4/MAC and IPv6 neighbor that is absent from this robust offline baseline.
