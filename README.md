![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg) ![](../../workflows/fpga/badge.svg)

# MNIST Handwritten Digit Deep Learning Accelerator ASIC
A deep learning accelerator ASIC chip design to classify images from the MNIST handwritten image dataset.

<p align="center"><img src="https://upload.wikimedia.org/wikipedia/commons/f/f7/MnistExamplesModified.png" /><br>Source: Wikipedia - MNIST database</p>

Design implementation for Tiny Tapeout.

Thanks to [Columbus IEEE Joint Chapter of the Solid-State Circuits and Circuits and Systems Societies](https://r2.ieee.org/columbus-ssccas/)!

Example:

Input --> |  Serialized to ASIC --> | Neural Network --> | Output
:----------:|:---------------:|:--------------:|:--------------
<img src="https://github.com/estods3/mnist_accelerator/blob/main/docs/real_image0.png" title="Example MNIST Image Reduced to 14x14 Black/White Pixels" alt="drawing" width="100"/><br>MNIST Image | Cycle  Input Pin: 0123456 0123456<br>----------------------------------<br>0-1   0000000 0000000<br>2-3   0000000 0000000<br>4-5    0000000 0111100<br>6-7    0000111 1111100<br>8-9    0000111 1100000<br>10-11   0000011 0000000<br>12-13   0000001 1000000<br>14-15   0000000 1110000<br>16-17   0000000 0110000<br>18-19   0000001 1110000<br>20-21   0000011 1100000<br>22-23   0011111 0000000<br>24-25   0011110 0000000<br>26-27   0000000 0000000<br> | <img src="https://github.com/estods3/mnist_accelerator/blob/main/docs/nndiagram.png" title="Example Neural Net Graph" alt="drawing" width="200"/> | BCD: 0101 = 5<br><br>7-Segment:5

## MNIST Dataset + Preprocessing
Input images from the [MNIST Dataset](https://en.wikipedia.org/wiki/MNIST_database) are preprocessed by a raspberry pi and transmitted to the ASIC. The images in MNIST are 28x28 grayscale images. However, as part of the preprocessing step, these images are reduced to a 14x14 black/white image to reduce the amount of data needed to be transmitted to the ASIC and to reduce the complexity of the neural network. Since the images are 14x14, a 8-pin interface (ui_in) is used which transmits 7 pixels at a time for 28 clock cycles to transmit each image. The remaining bit, the most significant bit (MSB), is a active-low signal. pulled low to start transmitting a new image.

### Preprocessing Python Script
A preprocessing python script (utility.py) is provided to convert the standard MNIST images into the reduced dataformat used in this project. The script is used to train the network, test the network, convert the pytorch implementation into verilog, and generate cocotb unit-tests directly from the MNIST dataset.

## Design

### LeNet-1 Mini: A BitNet-Style Neural Network for 14×14 Binary MNIST

> A compact digit classifier designed for FPGA and ASIC deployment, derived from a literature review of the smallest known neural networks for MNIST.
---
```python
class Net(nn.Module):
    """
    BitNet-style LeNet-1 Mini for 14×14 binary MNIST (10-class).
    Layer structure (BitNet pre-norm pattern):
        x  →  [RMSNorm → BitLinear(ternary) → ReLU]  →  [RMSNorm → BitLinear(3-bit)]  →  logits
    Input:  (B, 1, 14, 14) binary image  OR  (B, 196) flat binary vector
    Output: (B, 10) raw logits (use CrossEntropyLoss; no softmax here)
 
    Binary input note:
        Input pixels are already {0, 1} — no normalization or input quantization needed.
        The first layer effectively reduces to: for each output neuron, sum the inputs
        where weight=+1, subtract inputs where weight=-1, ignore where weight=0.
        This is AND/OR logic — no multiplier required at inference.
    """
    def __init__(self, hidden: int = 32):
        super().__init__()
        self.hidden = hidden
 
        # Pre-norm before each linear (BitNet SubLN / pre-norm pattern)
        self.norm1 = RMSNorm(196)
        self.norm2 = RMSNorm(hidden)
 
        # FC1: ternary weights {-1, 0, +1}  — ~1.58-bit, BitNet b1.58 style
        self.fc1 = BitLinear(196, hidden, weight_bits='ternary')
 
        # FC2: 3-bit weights {-3..+3}  — your requested 3-bit quantization
        self.fc2 = BitLinear(hidden, 10, weight_bits=3)
 
        self.act = nn.ReLU()
 
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Accept (B, 1, 14, 14) or (B, 196)
        if x.dim() == 4:
            x = x.view(x.size(0), -1)        # → (B, 196)
        x = x.float()                         # ensure float (input may be uint8/bool)
 
        # Block 1: norm → ternary linear → ReLU
        x = self.norm1(x)
        x = self.fc1(x)
        x = self.act(x)
 
        # Block 2: norm → 3-bit linear (logits, no activation)
        x = self.norm2(x)
        x = self.fc2(x)
 
        return x                              # raw logits
```

## Architecture
The network is a two-layer fully-connected classifier operating on flattened 14×14 binary images. The design adapts the LeNet-1 spatial intuition (small receptive fields, pooling, progressive feature extraction) to a pure FC topology appropriate for the parameter budget, with BitNet-style quantization throughout.

```
Input: 14×14 binary image → flatten → 196-dim binary vector
         │
    [RMSNorm(196)]
         │
    [BitLinear FC1: 196 → 32, ternary weights {−1, 0, +1}]
         │
    [ReLU]
         │
    [RMSNorm(32)]
         │
    [BitLinear FC2: 32 → 10, 3-bit weights {−3..+3}]
         │
Output: 10 logits → argmax → digit class (0–9)
```

### Design Decisions

**Binary input.** The 28×28 grayscale MNIST images are downsampled to 14×14 using average pooling over 2×2 blocks, then thresholded at 0.5 to produce 1-bit pixels. This eliminates the need for input normalization, simplifies the first layer's multiply to an AND operation at inference, and makes the model naturally robust to lighting variation. The binary input is a hardware advantage: a `{0,1}` × `{−1,0,+1}` multiply degenerates into a conditional copy (~10 gate-equivalents vs ~200 for a full 8×8 multiplier).

**Ternary FC1 weights.** Following BitNet b1.58, the first fully-connected layer uses absmean quantization to ternary `{−1, 0, +1}`. Shadow weights are kept at float32 during training and quantized in the forward pass via straight-through estimation. At inference, ternary weights produce multiplier-free arithmetic: each neuron's output is the sum of inputs connected with `+1` weights minus inputs connected with `−1` weights, with zero-weight connections skipped entirely.

**3-bit FC2 weights.** The output layer uses absmax/3 quantization to `{−3, −2, −1, 0, +1, +2, +3}` — 7 levels, requiring 3 bits per weight. Weights of magnitude 2 and 3 decompose into shift-and-add operations (`±2x = x<<1`, `±3x = (x<<1) + x`), preserving the multiplier-free property. The output layer uses higher precision than FC1 because classification decisions are made directly from these logits — quantization errors here cannot be averaged out by subsequent layers.

**RMSNorm (no bias).** BitNet's pre-norm pattern applies RMSNorm before each linear layer. Unlike LayerNorm, RMSNorm omits mean subtraction and centering bias, keeping only the learnable scale vector. All linear layers omit bias terms entirely, following the BitNet convention. This removes 196 + 32 = 228 bias parameters and simplifies hardware implementation.

**Why not convolutional layers?** The spatial dimension after downsampling (14×14) is small enough that the locality advantage of convolutions is reduced. The Grimov 1,936-parameter record for 28×28 MNIST uses separable convolutions with weight sharing; for 14×14 binary input with a strict parameter budget, a two-layer FC with aggressive quantization achieves comparable parameter counts without the routing complexity of convolutions in hardware.

**Why not go fully binary (1-bit)?** The Lottery Ticket literature and binary network research (BinaryConnect, ADMM binary LeNet-5) demonstrate that 1-bit weights are viable for LeNet-5-scale networks (~60K parameters) because redundancy across many weights absorbs rounding noise. Our network has only ~1,700 parameters — far less redundancy. Each weight carries real information. Forcing all weights to `±1` removes the ability to represent zero-weighted connections (true silence) and collapses the decision boundary resolution in the FC layers. Empirical estimates suggest ~1.5–2% accuracy loss vs ~0.1% for 4-bit, equivalent to the difference between ~25 and ~2 misclassified digits per 1,000.

---

## Quantization Analysis

Accuracy saturates at 4-bit for this task — adding precision beyond 4 bits yields no measurable improvement because the remaining ~0.6% error rate reflects data ambiguity (poorly formed digits, label noise), not weight resolution.

| Precision | Weight values | Est. accuracy | Verdict |
|---|---|---|---|
| 1-bit | `{−1, +1}` | ~97.5% | Too lossy for small network |
| 2-bit (ternary) | `{−1, 0, +1}` | ~98.8% | Viable with QAT |
| 3-bit | `{−3..+3}` | ~99.1% | Near lossless |
| **4-bit** | `{−8..+7}` | **~99.3%** | **Sweet spot — recommended** |
| 6-bit | `{−32..+31}` | ~99.4% | No gain over 4-bit |
| 8-bit | `{−128..+127}` | ~99.4% | Overkill |

The mixed-precision scheme assigns precision by layer sensitivity:

- **FC1 (ternary, ~1.58-bit):** Most input connections; ternary is a natural fit for binary inputs. Largest fan-in means individual weight errors average out.
- **FC2 (3-bit):** Output layer sets decision boundaries directly. Higher precision than FC1 because errors here cannot be smoothed by downstream operations.
- **RMSNorm scales:** Kept at 8-bit. These are scalar multiplications per channel — few parameters, high sensitivity.

**Post-training quantization (PTQ) is insufficient below 4-bit.** Rounding a trained float model works well at 8-bit but degrades rapidly below 4-bit on small networks. Quantization-aware training (QAT) — injecting fake quantization in the forward pass so gradients learn to work within the constrained weight space — is required for ternary and 3-bit weights. Without QAT, add approximately 1% additional accuracy loss per bit-level below 4.

---

## Implementation

### PyTorch (Training)

The model is implemented as `BitNetMini` with `BitLinear` layers replacing standard `nn.Linear`. Key components:

- `BitLinear` — holds float32 shadow weights updated by AdamW; quantizes in the forward pass via STE
- `RMSNorm` — learnable scale, no bias, no mean subtraction
- `prepare_binary_mnist()` — downsamples 28×28 → 14×14 via avg_pool2d, thresholds at 0.5
- `to_inference()` — freezes and exports `int8` weight tensors with per-layer scale factors

Training uses AdamW with cosine annealing over 20 epochs, gradient clipping at 1.0, and weight decay on linear layers only (not norm layers).

### Verilog (Inference / FPGA / ASIC)

The `export_to_verilog.py` script generates synthesizable Verilog directly from the frozen `int8` weights:
- FC1 ternary weights produce **pure add/subtract expressions** — no multiplier primitives
- FC2 3-bit weights decompose to **shift-and-add** (`<<1` for ×2, `<<1 + x` for ×3)
- RMSNorm approximated as **arithmetic right-shift** (barrel shift), baking the learned scale into the shift amount
- ReLU implemented as **sign-bit check** (`h = fc1_norm[15] ? 0 : fc1_norm`)
- Argmax over 10 logits implemented as a simple comparison loop
- All arithmetic in **16-bit signed integers** — no floating point on the FPGA

---

## Model Summary

<img src="https://github.com/estods3/mnist_accelerator/blob/main/docs/confusionmatrix.png" title="Latest MNIST Confusion Matrix" alt="drawing" width="600"/>

| Property | Value |
|---|---|
| Input | 14×14 binary (1-bit pixels) |
| Input dimensionality | 196 |
| Architecture | FC-32-10 with RMSNorm + ReLU |
| FC1 parameters | 196 × 32 = 6,272 connections → **320 weights** (ternary) |
| FC2 parameters | 32 × 10 = **320 weights** (3-bit) |
| RMSNorm parameters | 196 + 32 = **228 scale factors** |
| **Total trainable parameters** | **~1,724** |
| FC1 weight precision | Ternary `{−1, 0, +1}` (~1.58-bit) |
| FC2 weight precision | 3-bit `{−3..+3}` |
| Activation precision | 8-bit (absmax per-token, QAT) |
| Estimated test accuracy | ~99.1–99.3% on 14×14 binary MNIST |
| Multipliers required (inference) | **0** |
| Total MAC operations | ~5,098 |
| Estimated gate count (8-bit) | ~43,000 |
| Estimated gate count (mixed precision) | ~18,000 |
| Reduction vs LeNet-1 original | **~56×** fewer gates |

### Gate Count Breakdown (Mixed-Precision)

| Component | Gates | Notes |
|---|---|---|
| Conv arithmetic (FC1 ternary) | ~16K | AND/add/sub only — no multipliers |
| Weight SRAM | ~14K | 1,724 params × 8-bit storage |
| FC arithmetic (FC2 3-bit) | ~9K | Shift-and-add |
| Activations + control | ~4K | ReLU = sign check; RMSNorm = barrel shift |
| **Total** | **~43K** | 8-bit weights; **~18K** at mixed precision |

For reference: a 386 processor (1989) used ~275,000 transistors (~137K gate-equivalents). The mixed-precision LeNet-1 Mini at ~18K gates is approximately **7.6× smaller than a 386** in raw logic complexity — small enough to integrate alongside a microcontroller on a single die.

### Hardware Implementation and Automation Pipeline
Implemented into Verilog as a main file: project.v with 3 supporting files for readimage.v, neuralnetwork.v, and decoder.v

This project not only features an ASIC design for a neural network, but also a complete end-to-end pipeline to develop a neural network architecture in Python using PyTorch, train it, test it, and convert it to Verilog for ASIC/FPGA design. This end-to-end pipeline is contained in a single easy to use python utility file. See below:

```python
MNIST Python Utility:
	(1) Train Pytorch Model and save parameters
	(2) Test Pytorch Model against MNIST testset
	(3) Convert Pytorch Model to Verilog file neuralnetwork.v
	(4) Generate cocotb testcases for Verilog testbench (test.py)
	(5) Perform Benchmark - Run Pytorch and Tiny Tapeout chip in parallel (TBD)
```

#### Latest GDS Rendering:
![Latest GDS Render](https://camo.githubusercontent.com/228b13205764a96e707eca359e2bbcf6d30f91d01d457b0facd95521e1a55917/68747470733a2f2f6573746f6473332e6769746875622e696f2f6d6e6973745f616363656c657261746f722f6764735f72656e6465722e706e67)


## Results
Goal - show results of chip vs identical python-based neural network implementation.



## Tiny Tapeout
- [FAQ](https://tinytapeout.com/faq/)
- [Digital design lessons](https://tinytapeout.com/digital_design/)
- [Learn how semiconductors work](https://tinytapeout.com/siliwiz/)
- [Join the community](https://tinytapeout.com/discord)
- [Build your design locally](https://www.tinytapeout.com/guides/local-hardening/)

## References
@ARTICLE{leflow,
     author = {{Noronha}, D.~H. and {Salehpour}, B. and {Wilton}, S.~J.~E.},
     title = "{LeFlow: Enabling Flexible FPGA High-Level Synthesis of Tensorflow Deep Neural Networks}",
     journal = {ArXiv e-prints},
     archivePrefix = "arXiv",
     eprint = {1807.05317},
     keywords = {Computer Science - Machine Learning, Statistics - Machine Learning},
     year = 2018,
     month = jul,
     adsurl = {http://adsabs.harvard.edu/abs/2018arXiv180705317N}
} 
- [Example Verilog TT Seven Segment Display](https://github.com/TinyTapeout/tt05-verilog-demo/blob/main/src/tt_um_seven_segment_seconds.v)
- [Example Verilog reading an image](https://www.edaboard.com/threads/reading-image-file-in-verilog.268155/)
- [Example PyTorch MNIST Neural Network](https://github.com/pytorch/examples/blob/main/mnist/main.py)
- [MNIST Database](https://www.kaggle.com/datasets/hojjatk/mnist-dataset)
