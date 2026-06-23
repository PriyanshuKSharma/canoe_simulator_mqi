# CAN and DBC Documentation

## Purpose

The DBC file defines how raw CAN payload bytes map to engineering signals. The simulator uses this file both to encode simulated values and to decode received CAN frames for display.

DBC file:

```text
backend/bms.dbc
```

## Messages

| CAN ID | Decimal ID | Message | Length | Sender |
| --- | ---: | --- | ---: | --- |
| `0x100` | 256 | `BMS_Status` | 8 bytes | BMS |
| `0x101` | 257 | `BMS_PackVals` | 8 bytes | BMS |
| `0x102` | 258 | `BMS_Temps` | 8 bytes | BMS |

## `BMS_Status`

| Signal | Purpose | Unit |
| --- | --- | --- |
| `BMS_SOC` | Battery state of charge | `%` |
| `BMS_State` | BMS operating state | none |
| `BMS_ErrorFlags` | Bitmask of active faults | none |
| `BMS_Counter` | Rolling frame counter | none |
| `BMS_Checksum` | Simplified checksum placeholder | none |

State values:

| Value | State |
| ---: | --- |
| 0 | Init |
| 1 | Ready |
| 2 | Charging |
| 3 | Discharging |
| 4 | Fault |
| 5 | Shutdown |

Error flags:

| Bit | Fault |
| ---: | --- |
| 0 | Over-voltage |
| 1 | Under-voltage |
| 2 | Over-temperature |
| 3 | Under-temperature |
| 4 | Communication fault |

## `BMS_PackVals`

| Signal | Purpose | Unit |
| --- | --- | --- |
| `BMS_PackVoltage` | Total pack voltage | `V` |
| `BMS_PackCurrent` | Pack current, positive for charge and negative for discharge | `A` |
| `BMS_AvgCellVolt` | Average cell voltage | `V` |
| `BMS_CellVoltDev` | Cell voltage spread/deviation | `V` |

## `BMS_Temps`

| Signal | Purpose | Unit |
| --- | --- | --- |
| `BMS_MaxCellTemp` | Maximum measured cell temperature | `C` |
| `BMS_MinCellTemp` | Minimum measured cell temperature | `C` |
| `BMS_AvgCellTemp` | Average cell temperature | `C` |
| `BMS_TempSensorCount` | Number of temperature sensors represented | none |

## Simulation Rate

The backend sends three CAN frames every 100 ms:

```text
BMS_Status
BMS_PackVals
BMS_Temps
```

This produces an expected message rate of about 30 messages per second.

