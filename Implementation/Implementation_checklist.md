## Implementation Checklist

### `src/Encryption/`
- [ ] `encrypt(plaintext, key_K)` — AES-256-CBC with random IV, output as base64 string
- [ ] `generate_random_grid(rows, cols)` — use `secrets` module (CSPRNG), printable ASCII only
- [ ] `embed_ciphertext(grid, ciphertext, stencil_coords)` — validate no out-of-bounds
- [ ] `grid_to_bytestream(grid)` — row-major flattening

### `src/keygen/`
- [ ] `generate_stencil_coords(n_chars, rows, cols)` — CSPRNG, ensure uniqueness
- [ ] `generate_permutation(n)` — random σ via Fisher-Yates with `secrets`
- [ ] `generate_secret_key(stencil_coords, partition, permutation, reading_order, key_K)`
- [ ] `serialize_secret_key()` + `deserialize_secret_key()` — JSON + base64

### `src/Decryption/`
- [ ] `extract_bytestream(byte_array, stencil_coords, cols)` — Mode A
- [ ] `decrypt(ciphertext, secret_key, ...)`

### `test/`
- [ ] Round-trip: `decrypt(encrypt("HELLO")) == "HELLO"`
- [ ] Grid encoding/decoding: chars at stencil positions match ciphertext exactly
- [ ] Byte extraction: `extract_bytestream` recovers correct chars