# The Encryption - Decryption implementation idea

### Step 1: **Encrypt the plain text First (Level 1 encryption)**

Using Classical encryption schemes: MHKC/AES with crypto secret key K
```
"HELLO" → [Encryption] → "Xk9mP"
```

### Step 2: ** Steganographic Encryption (Level 2 encryption)** 

Security through obscurity / Grid hiding technique

**Fill Grid with Random Letters encrypted text from Step 1**

```
X Q Z M P T R N S V B W K D F G C Y A I U E
K R X N A D M L P Q S Z T Z B F Y W C V G U  ← 'X' hidden here
F Y k W S C Q N B M K P R T Z A D V L G I H  ← 'k' hidden here  
J U 9 m P I V N T Q R S W V X B A F D C H T  ← '9mP' hidden here
Z M K P N S T Q R W X B A D F C V Y G U E I
Q T W R S B N K M P L A X Z Y D F V G C H U
... (assume 100 more rows of random letters!)
```

### Step 3: **Generate Secret Key S**

According to the paper, the secret key contains:
```
Secret Key S = {
  1. Stencil Set SRl (chosen shapes)
  2. Bijection function g (maps partitions to stencils)
  3. MHKC/AES crypto secret key K
  4. Permutation σ 
  5. Starting position
  ...
}
```

### Step 4: **Transmission/Reception channel - Communication network**
1. **The grid** (as byte stream over network(Byte stream implementation) or as physical paper(OCR implementation))


### Step 5: **Steganographic Decryption (Level 1 decryption) **
Input: 
  1. Obscure Grid
  2. Assume the receiver already has : **The secret key S** (stencil indices/coordinates + crypto key)

Output:
  Cipher text - "Xk9mP"

### Step 6: **Decrypt the Cipher text (Level 2 decryption) **

Using Classical decryption schemes: MHKC/AES with crypto secret key K

"Xk9mP" → [Decryption] → "HELLO"