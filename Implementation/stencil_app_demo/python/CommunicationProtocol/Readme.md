# CommunicationProtocol Module

> See [Developer Guide](../../Developer_Guide.md) for the full system overview.

---

## Purpose

This module handles **transmission and reception of the grid bytestream** — the foundational layer for communication protocol research.

It is a dedicated research space for implementing different grid transmission mechanisms (Mode A: byte stream over network, Mode B: OCR/camera — and future modes). Each protocol gets its own file here.

---

## Files

| File | Responsibility |
|---|---|
| `bytestream_protocol.py` | Mode A: transmit/receive grid as a raw byte stream |

> **Pattern for future protocols:** each new transmission mode adds its own `<mode>_protocol.py` here.  
> e.g. `ocr_protocol.py` (Mode B: camera + OCR), `fax_protocol.py`, `qr_protocol.py`

---

## `bytestream_protocol.py`

```python
def grid_to_bytestream(grid: Grid) -> bytes:
    """
    Flatten the 2D grid into a byte stream for transmission.
    - Input: grid (Grid, ciphertext-embedded)
    - Output: bytes object.
    - Implementation: b''.join(grid.data)  — each row is already a bytearray.
    - Note: Equivalent byte index: grid.data[row][col] == bytestream[row * cols + col]
    """

def transmit(bytestream: bytes) -> None:
    """
    Transmit the grid bytestream to the receiver (Mode A).
    - Input: bytestream (bytes) — flattened grid from grid_to_bytestream()
    - TODO: implement actual transport (TCP socket, HTTP, message queue, etc.)
    """

def receive_bytestream() -> bytes:
    """
    Receive the grid bytestream from the sender (Mode A).
    - Output: bytes — raw grid bytestream
    - TODO: implement actual transport matching transmit()
    """

def get_grid_dimensions() -> Tuple[int, int]:
    """
    Return the (rows, cols) dimensions of the transmitted grid.
    - Output: (rows, cols) tuple
    - Note: both sender and receiver must agree on grid dimensions out-of-band
      (or dimensions can be prepended to the bytestream as a header).
    """
```

---

## Research Direction

The `transmit()` / `receive_bytestream()` calls in `stencil_app/sender.py` and `stencil_app/receiver.py` are placeholders — the actual transport mechanism is an open research question:

| Mode | File | Notes |
|---|---|---|
| **Mode A: Byte stream** | `bytestream_protocol.py` | TCP socket, HTTP POST, message queue — grid in memory |
| **Mode B: OCR / Camera** | `ocr_protocol.py` *(future)* | Grid printed on paper; camera zoom + OCR extracts chars |
| Fax | `fax_protocol.py` *(future)* | Grid transmitted as image via fax, OCR on receive |
| QR code | `qr_protocol.py` *(future)* | Grid encoded as QR, scanned on receive |

---

> For how transmission is used in the application layer, see [stencil_app/Readme.md](../../../stencil_app/Readme.md).  
> For the two implementation modes overview, see [Developer Guide — Two Implementation Modes](../../Developer_Guide.md#two-implementation-modes).
