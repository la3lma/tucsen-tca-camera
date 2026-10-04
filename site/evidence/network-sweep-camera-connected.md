# Network sweep while the camera was connected to the Raspberry Pi

Captured from the macOS workstation on `en0` at 2026-09-26T19:47:26Z
(2026-09-26T21:47:26+0200). The Raspberry Pi was powered and connected to the
LAN, with the microscope camera connected by USB.

Important: unplugging only the USB camera will not normally change the Pi's
network address. For a useful differential sweep, disconnect the Pi from the
network or power it off while leaving the other LAN devices unchanged.

## Active IPv4/MAC pairs (`arp-scan --interface=en0 --localnet`)

| IPv4 | MAC | Reported vendor |
|---|---|---|
| 10.0.0.1 | 9c:a2:f4:6c:f1:36 | TP-Link Corporation Limited |
| 10.0.0.2 | d0:14:11:90:53:b2 | Airthings |
| 10.0.0.4 | c8:2e:18:f9:ae:f4 | Unknown |
| 10.0.0.6 | 8c:86:1e:64:1b:93 | Apple, Inc. |
| 10.0.0.7 | 10:20:ba:43:a6:24 | Unknown |
| 10.0.0.17 | f8:71:a6:b7:aa:f4 | Unknown |
| 10.0.0.21 | 68:63:59:db:18:e4 | Advanced Digital Broadcast SA |
| 10.0.0.32 | 78:45:58:e5:5b:58 | Ubiquiti Networks Inc. |
| 10.0.0.43 | 94:dd:f8:28:ee:7c | Brother Industries, LTD. |
| 10.0.0.45 | 1c:69:7a:4c:50:37 | EliteGroup Computer Systems Co., LTD |
| 10.0.0.50 | c6:82:18:24:5f:2c | Locally administered |
| 10.0.0.53 | 34:2f:bd:e3:61:e3 | Nintendo Co., Ltd. |
| 10.0.0.59 | 30:05:5c:4d:8c:a5 | Brother Industries, LTD. |
| 10.0.0.63 | d4:f3:2d:fb:de:61 | Unknown |
| 10.0.0.74 | a8:3f:a1:7c:95:a5 | Plejd AB |
| 10.0.0.80 | 9c:75:6e:39:b8:7c | Ajax Systems DMCC |
| 10.0.0.93 | 30:56:0f:5e:d0:fc | Unknown; known host `agogo` |
| 10.0.0.95 | ca:68:03:29:97:8a | Locally administered; confirmed `Gourd.local` |
| 10.0.0.123 | 90:09:d0:a0:bb:a2 | Synology Incorporated |
| 10.0.0.138 | f4:4d:5c:57:28:d0 | Zyxel Communications Corporation |

`arp-scan` reported 20 responders. None used a Raspberry Pi Foundation OUI,
although a Pi may use a USB adapter or a locally administered/randomized MAC.

## IPv6 neighbor discovery

The all-nodes link-local multicast probe (`ping6 ff02::1%en0`) produced these
remote `en0` neighbors with complete MAC mappings in the numeric NDP table:

| IPv6 link-local | MAC |
|---|---|
| fe80::a4:1719:e433:83c0%en0 | d4:ce:40:38:5b:59 |
| fe80::8db:c33:5872:693f%en0 | 44:09:da:1a:ad:7f |
| fe80::14ea:f6e1:52b6:143a%en0 | 8c:86:1e:64:1b:93 |
| fe80::14f0:a4f9:5d3e:d0fc%en0 | c6:82:18:24:5f:2c |
| fe80::1811:d87e:bf2c:1fc9%en0 | f6:df:1c:cb:d8:0b |
| fe80::183c:b62a:9ace:141c%en0 | be:fb:77:6a:ea:db |
| fe80::1c38:373b:2a3:4bc1%en0 | 1e:de:e0:e9:0c:23 |
| fe80::1c7d:374b:1ecc:e1a8%en0 | ca:68:03:29:97:8a |
| fe80::1cc3:f54e:6ca2:4d68%en0 | f8:71:a6:b7:aa:f4 |
| fe80::3035:f174:ca61:3faa%en0 | 1c:69:7a:4c:50:37 |
| fe80::3256:fff:fe5:d0fc%en0 | 30:56:0f:5e:d0:fc |
| fe80::7a45:58ff:fee5:5b58%en0 | 78:45:58:e5:5b:58 |
| fe80::96dd:f8ff:fe28:ee7c%en0 | 94:dd:f8:28:ee:7c |
| fe80::aa3f:a1ff:fe7c:95a5%en0 | a8:3f:a1:7c:95:a5 |
| fe80::f64d:5cff:fe57:28d0%en0 | f4:4d:5c:57:28:d0 |

## SSH listeners

Parallel one-second TCP probes found port 22 open at:

- `10.0.0.13` — current workstation
- `10.0.0.32` — Dropbear 2020.81, Ubiquiti MAC; loaded keys rejected for
  `rmz`, `pi`, and `root`
- `10.0.0.93` — known Ubuntu host `agogo`
- `10.0.0.95` — authenticated with a loaded key and reported `Gourd.local`,
  Apple `arm64`

The historical SSH key for `rpios-16.local` was also stored under old IPv4
addresses `10.0.0.82` and `10.0.0.83`; neither address answered ARP or SSH in
this connected-state sweep.
