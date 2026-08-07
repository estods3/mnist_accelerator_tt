#
# Copyright (c) 2024 Evan Stoddart
# github.com/estods3
# SPDX-License-Identifier: Apache-2.0
#

from __future__ import print_function
import numpy as np
import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms, utils
from torch.optim.lr_scheduler import StepLR
import torch.quantization as quant
import textwrap
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, accuracy_score
import seaborn as sns

from data_preprocessor import preprocessor, generate_cocotb_tests

# Define a custom observer for 2-bit quantization
#
#
#
class TwoBitQuantizationObserver(quant.ObserverBase):
    def __init__(self, dtype=torch.qint8, quant_min=-2, quant_max=1):
        super().__init__(dtype=dtype)
        self.dtype = dtype
        self.quant_min = quant_min
        self.quant_max = quant_max

    def calculate_qparams(self):
        scale = 1.0
        zero_point = 0
        return scale, zero_point

    def forward(self, x):
        # Quantize to 2 bits
        return torch.clamp(x.round(), self.quant_min, self.quant_max)

######################################################################
# Neural Network Model                                               #
# --------------------                                               #
# Desc: pytorch neural network design used to classify MNIST images  #
# NOTE: The neural network defined here will be used to train, test, #
# and deploy to verilog for Tiny Tapeout Design.                     #
#                                                                    #
######################################################################
def ternary_quant(W: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """
    AbsMean ternary quantization (BitNet b1.58).
    Scales W by 1/mean(|W|), rounds to nearest in {-1, 0, +1}.
    Returns (W_ternary, scale) where scale = mean(|W|).
    Straight-through: gradient flows through round() unchanged.
    """
    scale = W.abs().mean().clamp(min=1e-8)
    W_scaled = W / scale
    # STE: round in forward, identity in backward
    W_q = (W_scaled.round().clamp(-1, 1) - W_scaled).detach() + W_scaled
    return W_q, scale
 
 
def int3_quant(W: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """
    3-bit signed integer quantization: {-3, -2, -1, 0, +1, +2, +3}.
    Uses absmax scaling to fill the ±3 range, then rounds and clamps.
    7 levels → ceil(log2(7)) = 3 bits per weight.
    STE gradient through round+clamp.
    """
    scale = W.abs().max().clamp(min=1e-8) / 3.0
    W_scaled = W / scale
    W_q = (W_scaled.round().clamp(-3, 3) - W_scaled).detach() + W_scaled
    return W_q, scale
 
 
def activation_quant_8bit(x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Per-token 8-bit absmax activation quantization (BitNet b1.58 style).
    Quantizes to {-127..+127}, returns fake-quantized tensor and per-row scale.
    """
    scale = x.abs().max(dim=-1, keepdim=True).values.clamp(min=1e-8) / 127.0
    x_q = (x / scale).round().clamp(-127, 127)
    # STE: dequantize immediately so downstream sees real-valued tensor
    x_dq = (x_q - x / scale).detach() + x / scale
    return x_dq * scale, scale
 
 
# ─────────────────────────────────────────────
#  RMSNorm (BitNet uses this instead of LayerNorm; no bias, no mean subtraction)
# ─────────────────────────────────────────────
 
class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-8):
        super().__init__()
        self.eps = eps
        self.g = nn.Parameter(torch.ones(dim))   # learnable scale; no bias
 
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        rms = x.pow(2).mean(dim=-1, keepdim=True).add(self.eps).sqrt()
        return x / rms * self.g
 
 
# ─────────────────────────────────────────────
#  BitLinear — drop-in replacement for nn.Linear
# ─────────────────────────────────────────────
 
class BitLinear(nn.Module):
    """
    BitNet-style linear layer.
      weight_bits='ternary'  → {-1,0,+1}   (absmean, ~1.58-bit)
      weight_bits=3          → {-3..+3}     (absmax/3, true 3-bit)
    No bias (BitNet convention).
    Input activations are 8-bit absmax quantized per-token.
    Shadow weights stay float32 during training; only quantized in forward pass.
    """
    def __init__(self, in_features: int, out_features: int, weight_bits='ternary'):
        super().__init__()
        self.in_features  = in_features
        self.out_features = out_features
        self.weight_bits  = weight_bits
 
        # Shadow weights — always full precision, updated by optimizer
        self.weight = nn.Parameter(torch.empty(out_features, in_features))
        nn.init.kaiming_uniform_(self.weight, a=0.0, mode='fan_in', nonlinearity='relu')
 
        # No bias — BitNet removes all biases
 
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # 1. Quantize activations (8-bit absmax per token)
        x_q, x_scale = activation_quant_8bit(x)
 
        # 2. Quantize weights (ternary or 3-bit) with STE
        if self.weight_bits == 'ternary':
            W_q, w_scale = ternary_quant(self.weight)
        else:  # 3-bit
            W_q, w_scale = int3_quant(self.weight)
 
        # 3. Linear op on fake-quantized values
        out = F.linear(x_q, W_q)
 
        # 4. Rescale output by both scales (weight scale * activation max recovered downstream)
        #    In full BitNet this is a single fused scale; here we fold it in directly.
        out = out * w_scale
 
        return out
 
    @torch.no_grad()
    def freeze(self) -> dict:
        """
        Call after training to extract integer weights for deployment.
        Returns dict with integer weights and the scale factor.
        """
        if self.weight_bits == 'ternary':
            scale = self.weight.abs().mean().clamp(min=1e-8)
            W_int = self.weight.div(scale).round().clamp(-1, 1).to(torch.int8)
        else:
            scale = self.weight.abs().max().clamp(min=1e-8) / 3.0
            W_int = self.weight.div(scale).round().clamp(-3, 3).to(torch.int8)
        return {'W_int': W_int, 'scale': scale.item(), 'bits': self.weight_bits}
 
 
# ─────────────────────────────────────────────
#  BitNet Mini — main model
# ─────────────────────────────────────────────
#class BitNetMini(nn.Module):
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
 
    @torch.no_grad()
    def to_inference(self) -> dict:
        """
        Freeze and export integer weights for deployment (MCU / FPGA / ASIC).
        Returns a dict of layer weights as int8 tensors + scales.
        The frozen model needs only integer addition at inference — no multiplies.
        """
        return {
            'fc1': self.fc1.freeze(),   # int8 weights in {-1,0,+1}, scale float
            'fc2': self.fc2.freeze(),   # int8 weights in {-3..+3}, scale float
            'norm1_g': self.norm1.g.data.clone(),
            'norm2_g': self.norm2.g.data.clone(),
        }

#class Net(nn.Module):
#    def __init__(self):
#        super(Net, self).__init__()
#        self.quant = torch.quantization.QuantStub()
#        self.fc1 = nn.Linear(196, 32)
#        self.relu = nn.ReLU()
#        self.fc2 = nn.Linear(32, 10)
#        self.dequant = torch.quantization.DeQuantStub()
    
#    def forward(self, x):
#        x = x.view(-1, 196)
#        x = self.quant(x)
#        x = self.fc1(x)
#        x = self.relu(x)
#        x = self.fc2(x)
#        x = self.dequant(x)
#        return x

# Training Helper Function
# desc: perfom training on a model given the parameters
# inputs:
# returns: None
def train(args, model, device, train_loader, optimizer, epoch):
    model.train()
    criterion = nn.CrossEntropyLoss()

    # Logging, Training Visualization
    train_losses = []
    test_losses = []
    test_accuracies = []

    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        #loss = F.nll_loss(output, target)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % args.log_interval == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item()))
            if args.dry_run:
                break


        #TODO - keep track of training progression. create plots that display and save to files to be embedded in README
        #train_loss = running_loss / len(train_loader)
        #train_losses.append(train_loss)

        #test_loss = test_loss / len(test_loader)
        #test_losses.append(test_loss)
        
        #accuracy = 100 * correct / total
        #test_accuracies.append(accuracy)

# Testing Helper Function
# desc: test the model on a test set
# inputs:
# returns: none
def test(model, device, test_loader):
    model.eval()
    test_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            test_loss += F.nll_loss(output, target, reduction='sum').item()  # sum up batch loss
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    test_loss /= len(test_loader.dataset)

    print('\nTest set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n'.format(
        test_loss, correct, len(test_loader.dataset),
        100. * correct / len(test_loader.dataset)))

def make_optimizer(model: Net, lr: float = 1e-3, weight_decay: float = 0.01):
    """
    BitNet convention: optimize shadow weights only, no weight decay on norms.
    """
    decay_params = [p for n, p in model.named_parameters() if 'norm' not in n]
    nodecay_params = [p for n, p in model.named_parameters() if 'norm' in n]
    return torch.optim.AdamW([
        {'params': decay_params,   'weight_decay': weight_decay},
        {'params': nodecay_params, 'weight_decay': 0.0},
    ], lr=lr)

# Train and Save Model
# desc: sets up model, training/test sets, etc. and calls train()
# Inputs: None
# Returns: model, trained
def train_model():
    # Training Settings
    parser = argparse.ArgumentParser(description='PyTorch MNIST Example')
    parser.add_argument('--batch-size', type=int, default=64, metavar='N',help='input batch size for training (default: 64)')
    parser.add_argument('--test-batch-size', type=int, default=1000, metavar='N',help='input batch size for testing (default: 1000)')
    parser.add_argument('--epochs', type=int, default=15, metavar='N', help='number of epochs to train (default: 15)')
    parser.add_argument('--lr', type=float, default=0.01, metavar='LR', help='learning rate (default: 1.0)')
    parser.add_argument('--gamma', type=float, default=0.7, metavar='M',help='Learning rate step gamma (default: 0.7)')
    parser.add_argument('--no-cuda', action='store_true', default=False, help='disables CUDA training')
    parser.add_argument('--no-mps', action='store_true', default=False, help='disables macOS GPU training')
    parser.add_argument('--dry-run', action='store_true', default=False, help='quickly check a single pass')
    parser.add_argument('--seed', type=int, default=1, metavar='S', help='random seed (default: 1)')
    parser.add_argument('--log-interval', type=int, default=10, metavar='N', help='how many batches to wait before logging training status')
    parser.add_argument('--save-model', action='store_true', default=False, help='For Saving the current Model')
    args = parser.parse_args()
    use_cuda = not args.no_cuda and torch.cuda.is_available()
    use_mps = not args.no_mps and torch.backends.mps.is_available()

    torch.manual_seed(args.seed)

    if use_cuda:
        device = torch.device("cuda")
    elif use_mps:
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    train_kwargs = {'batch_size': args.batch_size}
    test_kwargs = {'batch_size': args.test_batch_size}
    if use_cuda:
        cuda_kwargs = {'num_workers': 1,
                       'pin_memory': True,
                       'shuffle': True}
        train_kwargs.update(cuda_kwargs)
        test_kwargs.update(cuda_kwargs)

    t = preprocessor()
    dataset1 = datasets.MNIST('../data', train=True, download=True, transform=t)
    dataset2 = datasets.MNIST('../data', train=False, transform=t)

    train_loader = torch.utils.data.DataLoader(dataset1,**train_kwargs)
    test_loader = torch.utils.data.DataLoader(dataset2, **test_kwargs)

    model = Net().to(device)

    #optimizer = optim.Adam(model.parameters(), lr=args.lr)
    #optimizer = optim.Adadelta(model.parameters(), lr=args.lr)
    optimizer = make_optimizer(model, lr=3e-3)

    #scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=20)


    # Example usage with quantization aware training
    #model.qconfig = quant.QConfig(
    #    activation=TwoBitQuantizationObserver,
    #    weight=TwoBitQuantizationObserver
    #)
    #model = quant.prepare(model)

    #model.qconfig = quant.get_default_qat_qconfig('fbgemm')   # 6% accuracy
    #model = quant.prepare_qat(model)

    # Train the model with quantization-aware training
    for epoch in range(1, args.epochs + 1):
        train(args, model, device, train_loader, optimizer, epoch)
        test(model, device, test_loader)
        scheduler.step()
    
    #model = quant.convert(model)

    # FP16 inference
    #model = model.half()  # Convert model to FP16

    #scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma)
    #for epoch in range(1, args.epochs + 1):
    #    #train(args, model, device, train_loader, optimizer, epoch)
    #    test(model, device, test_loader)
    #    scheduler.step()
    
    return model

# Test Model
# desc: sets up model, gets test set, etc. and calls test()
# Inputs: model - trained pytorch net()
# Returns: None
def test_model(model):
    # Testing Settings
    use_cuda = torch.cuda.is_available()
    use_mps = torch.backends.mps.is_available()
    test_kwargs = {'batch_size': 1000}
    torch.manual_seed(1)

    # Configuring Hardware Device
    if use_cuda:
        device = torch.device("cuda")
    elif use_mps:
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    if use_cuda:
        cuda_kwargs = {'num_workers': 1,
                       'pin_memory': True,
                       'shuffle': True}
        test_kwargs.update(cuda_kwargs)

    # Gather Test Set
    t = preprocessor()
    dataset2 = datasets.MNIST('../data', train=False, transform=t)
    test_loader = torch.utils.data.DataLoader(dataset2, **test_kwargs)

    # Test
    test(model, device, test_loader)

    # Test Results/Analytics
    # TODO - create plots that display and save to files to be embedded in README
    # TODO - issues with matplotlib plotting. core dumped
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)
            
            all_preds.extend(predicted.numpy())
            all_labels.extend(labels.numpy())
    
    # Calculate accuracy
    accuracy = accuracy_score(all_labels, all_preds)
    print(f"Test Accuracy: {accuracy * 100:.2f}%")
    
    # Create confusion matrix
    cm = confusion_matrix(all_labels, all_preds)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title('Confusion Matrix')
    plt.show()

# ─────────────────────────────────────────────
#  Step 1: Export weights from trained model
# ─────────────────────────────────────────────

def export_weights(checkpoint_path: str, output_path: str = 'bitnet_mini_weights.npz'):
    """Load checkpoint and save integer weights + scales as .npz"""
    model = Net(hidden=32)
    model.load_state_dict(torch.load(checkpoint_path, map_location='cpu', weights_only=True))
    model.eval()

    frozen = model.to_inference()

    # FC1: ternary weights as int8 in {-1, 0, +1}
    fc1_W   = frozen['fc1']['W_int'].numpy().astype(np.int8)   # (32, 196)
    fc1_s   = np.float32(frozen['fc1']['scale'])

    # FC2: 3-bit weights as int8 in {-3..+3}
    fc2_W   = frozen['fc2']['W_int'].numpy().astype(np.int8)   # (10, 32)
    fc2_s   = np.float32(frozen['fc2']['scale'])

    # RMSNorm gain vectors (used to adjust shift amount in hardware)
    norm1_g = frozen['norm1_g'].numpy().astype(np.float32)     # (196,)
    norm2_g = frozen['norm2_g'].numpy().astype(np.float32)     # (32,)

    np.savez(output_path,
             fc1_W=fc1_W, fc1_scale=fc1_s,
             fc2_W=fc2_W, fc2_scale=fc2_s,
             norm1_g=norm1_g, norm2_g=norm2_g)

    print(f"Saved weights to {output_path}")
    print(f"  FC1: {fc1_W.shape}  unique={np.unique(fc1_W).tolist()}  scale={fc1_s:.6f}")
    print(f"  FC2: {fc2_W.shape}  unique={np.unique(fc2_W).tolist()}  scale={fc2_s:.6f}")
    print(f"  Sparsity FC1: {(fc1_W == 0).mean():.1%} zeros")
    print(f"  Sparsity FC2: {(fc2_W == 0).mean():.1%} zeros")
    return fc1_W, fc1_s, fc2_W, fc2_s, norm1_g, norm2_g


# ─────────────────────────────────────────────
#  Step 2: Verilog code generators
# ─────────────────────────────────────────────

def ternary_weight_to_verilog_expr(weights_row: np.ndarray, input_signal: str) -> str:
    """
    Convert one row of ternary weights into a Verilog add/sub expression.
    weights_row: int8 array of {-1, 0, +1}, length = fan_in
    input_signal: name of the input wire/reg array, e.g. 'x'
    Result: 'x[0] + x[3] - x[5] - x[7] + ...'  (zeros are simply skipped)
    This is MULTIPLIER-FREE — just conditional adds/subs.
    """
    terms = []
    for i, w in enumerate(weights_row):
        if w == 1:
            terms.append(f"{input_signal}[{i}]")
        elif w == -1:
            terms.append(f"(-{input_signal}[{i}])")
    if not terms:
        return "16'sd0"
    return " + ".join(terms)


def int3_weight_to_verilog_expr(w: int, var: str) -> str:
    """
    Convert a 3-bit weight ∈ {-3..+3} into shift-and-add Verilog.
    Decomposition (all shift-and-add, no multiply):
      ±1 → ±var
      ±2 → ±(var << 1)
      ±3 → ±(var << 1) ± var   (i.e. ±2x ± x)
    """
    abs_w = abs(w)
    sign  = '' if w > 0 else '-'
    if abs_w == 0:
        return "16'sd0"
    elif abs_w == 1:
        return f"{sign}{var}"
    elif abs_w == 2:
        return f"{sign}({var} <<< 1)"
    elif abs_w == 3:
        if w > 0:
            return f"({var} <<< 1) + {var}"
        else:
            return f"-(({var} <<< 1) + {var})"
    return f"16'sd0"


def generate_verilog(fc1_W, fc2_W, norm1_g, norm2_g, output_path='bitnet_mini.v'):
    """
    Generate synthesizable Verilog for the full BitNetMini forward pass.

    Design choices:
      - Fully combinational — no clock. Add pipeline registers for high-freq targets.
      - Input: 196-bit packed binary vector `pixel_in`
      - Output: 10 × 16-bit signed logits `logit_out[0..9]`
      - RMSNorm approximated as arithmetic right-shift (barrel shift).
        The shift amount is chosen to match the learned norm scale * weight scale.
      - All intermediate signals are 16-bit signed to prevent overflow on MNIST-sized inputs.
    """

    N_IN   = 196   # 14×14
    N_H    = 32    # hidden
    N_OUT  = 10    # digits

    # Determine RMSNorm shift amounts from the learned gain vectors.
    # norm1 operates on 196-dim input, expected RMS ≈ 1 for binary input with ~50% ones.
    # We bake norm gain into a right-shift to approximate division by RMS.
    # Shift = round(log2(N_IN^0.5)) for binary input (RMS of 196-dim binary ≈ sqrt(98) ≈ 9.9)
    # Then adjust by mean norm gain. This is an approximation — tune empirically.
    NORM1_SHIFT = int(round(np.log2(np.sqrt(N_IN) / np.mean(norm1_g))))
    NORM2_SHIFT = int(round(np.log2(np.sqrt(N_H)  / np.mean(norm2_g))))
    NORM1_SHIFT = max(0, min(NORM1_SHIFT, 7))
    NORM2_SHIFT = max(0, min(NORM2_SHIFT, 7))
    NORM1_SHIFT = 0 #TODO
    NORM2_SHIFT = 0 #TODO

    lines = []
    a = lines.append   # shorthand

    # ── File header ──
    a("// ============================================================")
    a("// BitNetMini — 14×14 binary MNIST → 10-class digit recognizer")
    a("// Auto-generated by export_to_verilog.py")
    a("// Weights: FC1 ternary {-1,0,+1} | FC2 3-bit {-3..+3}")
    a("// Arithmetic: addition/subtraction + shifts only — no multipliers")
    a("// ============================================================")
    a("")
    a("`timescale 1ns/1ps")
    a("")

    # ── Top module ──
    a("module bitnet_mini (")
    a(f"    input  wire [{N_IN-1}:0]       pixel_in,   // 196 binary pixels, LSB = pixel[0]")
    a(f"    output wire signed [15:0]      logit_out [0:{N_OUT-1}]  // 10 raw logits")
    a(");")
    a("")

    # ── Input wires (one per pixel) ──
    a("    // ── Expand packed input to individual signed wires ──")
    a(f"    wire signed [15:0] x [{N_IN-1}:0];")
    a(f"    genvar gi;")
    a(f"    generate")
    a(f"        for (gi = 0; gi < {N_IN}; gi = gi + 1) begin : input_expand")
    a(f"            assign x[gi] = {{15'b0, pixel_in[gi]}};  // zero-extend 1-bit to 16-bit signed")
    a(f"        end")
    a(f"    endgenerate")
    a("")

    # ── FC1: ternary dot products ──
    a("    // ── FC1: 196→32 ternary linear ──")
    a(f"    wire signed [15:0] fc1_raw [{N_H-1}:0];")
    for j in range(N_H):
        row_reversed = fc1_W[j][::-1]   # reverse pixel order to match ImageReader packing
        expr = ternary_weight_to_verilog_expr(row_reversed, 'x')
        a(f"    assign fc1_raw[{j:2d}] = {expr};")
    a("")

    # ── RMSNorm1 approximation: arithmetic right-shift ──
    a(f"    // ── RMSNorm1 ≈ arithmetic right-shift by {NORM1_SHIFT} ──")
    a(f"    wire signed [15:0] fc1_norm [{N_H-1}:0];")
    if NORM1_SHIFT > 0:
        a(f"    genvar gn1;")
        a(f"    generate")
        a(f"        for (gn1 = 0; gn1 < {N_H}; gn1 = gn1 + 1) begin : norm1_shift")
        a(f"            assign fc1_norm[gn1] = fc1_raw[gn1] >>> {NORM1_SHIFT};")
        a(f"        end")
        a(f"    endgenerate")
    else:
        a(f"    genvar gn1;")
        a(f"    generate")
        a(f"        for (gn1 = 0; gn1 < {N_H}; gn1 = gn1 + 1) begin : norm1_passthru")
        a(f"            assign fc1_norm[gn1] = fc1_raw[gn1];")
        a(f"        end")
        a(f"    endgenerate")
    a("")

    # ── ReLU ──
    a("    // ── ReLU ──")
    a(f"    wire signed [15:0] h [{N_H-1}:0];")
    a(f"    genvar gr;")
    a(f"    generate")
    a(f"        for (gr = 0; gr < {N_H}; gr = gr + 1) begin : relu")
    a(f"            assign h[gr] = fc1_norm[gr][15] ? 16'sd0 : fc1_norm[gr];  // h = max(0, x)")
    a(f"        end")
    a(f"    endgenerate")
    a("")

    # ── FC2: 3-bit weights, shift-and-add ──
    a("    // ── FC2: 32→10, 3-bit weights (shift-and-add, no multipliers) ──")
    a(f"    wire signed [15:0] fc2_raw [{N_OUT-1}:0];")
    for k in range(N_OUT):
        terms = []
        for j in range(N_H):
            w = int(fc2_W[k, j])
            if w != 0:
                terms.append(int3_weight_to_verilog_expr(w, f"h[{j}]"))
        expr = " + ".join(terms) if terms else "16'sd0"
        # Wrap long lines
        if len(expr) > 100:
            chunks = textwrap.wrap(expr, width=100, break_long_words=False, break_on_hyphens=False)
            wrapped = ("\n" + " " * 24).join(chunks)
            a(f"    assign fc2_raw[{k}] = {wrapped};")
        else:
            a(f"    assign fc2_raw[{k}] = {expr};")
    a("")

    # ── RMSNorm2 approximation ──
    a(f"    // ── RMSNorm2 ≈ arithmetic right-shift by {NORM2_SHIFT} ──")
    a(f"    genvar gn2;")
    a(f"    generate")
    a(f"        for (gn2 = 0; gn2 < {N_OUT}; gn2 = gn2 + 1) begin : norm2_shift")
    if NORM2_SHIFT > 0:
        a(f"            assign logit_out[gn2] = fc2_raw[gn2] >>> {NORM2_SHIFT};")
    else:
        a(f"            assign logit_out[gn2] = fc2_raw[gn2];")
    a(f"        end")
    a(f"    endgenerate")
    a("")
    a("endmodule")
    a("")

    # ── Argmax module ──
    a("// ============================================================")
    a("// Argmax: finds the digit with highest logit")
    a("// ============================================================")
    a("module argmax10 (")
    a("    input  wire signed [15:0] logit [0:9],")
    a("    output reg  [3:0]         digit_out   // 0-9")
    a(");")
    a("    integer i;")
    a("    reg signed [15:0] max_val;")
    a("    always @(*) begin")
    a("        max_val   = logit[0];")
    a("        digit_out = 4'd0;")
    a("        for (i = 1; i < 10; i = i + 1) begin")
    a("            if (logit[i] > max_val) begin")
    a("                max_val   = logit[i];")
    a("                digit_out = i[3:0];")
    a("            end")
    a("        end")
    a("    end")
    a("endmodule")
    a("")

    # ── Top-level wrapper with argmax ──
    a("// ============================================================")
    a("// Top wrapper: pixels in → digit out")
    a("// ============================================================")
    a("module bitnet_mini_top (")
    a("    input  wire [195:0] pixel_in,")
    a("    output wire [3:0]   digit_out")
    a(");")
    a("    wire signed [15:0] logits [0:9];")
    a("    bitnet_mini  nn  (.pixel_in(pixel_in), .logit_out(logits));")
    a("    argmax10     ax  (.logit(logits),       .digit_out(digit_out));")
    a("endmodule")
    a("")

    verilog_src = "\n".join(lines)
    Path(output_path).write_text(verilog_src)
    print(f"Verilog written to {output_path}  ({len(lines)} lines)")
    return verilog_src

# ─────────────────────────────────────────────
#  Step 4: Print synthesis hints
# ─────────────────────────────────────────────

def print_synthesis_notes(fc1_W, fc2_W):
    n_fc1_nonzero = np.count_nonzero(fc1_W)
    n_fc2_nonzero = np.count_nonzero(fc2_W)
    total_ops = n_fc1_nonzero + n_fc2_nonzero * 2  # 3-bit ≈ 2 adds per weight avg

    print("\n" + "="*60)
    print("SYNTHESIS NOTES")
    print("="*60)
    print(f"FC1 non-zero weights : {n_fc1_nonzero} / {fc1_W.size}  "
          f"({n_fc1_nonzero/fc1_W.size:.0%})")
    print(f"FC2 non-zero weights : {n_fc2_nonzero} / {fc2_W.size}  "
          f"({n_fc2_nonzero/fc2_W.size:.0%})")
    print(f"Total add/sub ops    : ~{total_ops}")
    print(f"Multipliers needed   : 0")
    print()
    print("Synthesis flow (Xilinx Vivado / Intel Quartus):")
    print("  1. vivado -mode batch -source synth.tcl")
    print("     (or quartus_map --compile bitnet_mini.v)")
    print("  2. Target: any Artix-7 or Cyclone V or larger")
    print("  3. Expected LUT usage: ~500-2000 LUTs (Artix-7 7-input LUTs)")
    print("  4. Expected fMAX:      >200 MHz combinational (no registers)")
    print("  5. For pipelined version: insert FF stages between FC1→ReLU→FC2")
    print()
    print("Simulation (Icarus Verilog, free):")
    print("  iverilog -o sim bitnet_mini.v bitnet_mini_tb.v")
    print("  vvp sim")
    print("  gtkwave bitnet_mini.vcd   # view waveforms")
    print()
    print("RMSNorm approximation warning:")
    print("  The shift-based norm approximation loses accuracy vs float.")
    print("  For better results, implement a lookup table for norm scales")
    print("  or use a fixed-point multiplier for the norm gain vector.")
    print("="*60)


# Convert Model to Verilog
# Desc: Convert Pytorch model into a hardware description language such as Verilog
# Inputs: None
# Returns: None
def convert_model_to_verilog():
    print("Converting model to verilog")
    # Export integer weights
    model = Net()
    model.load_state_dict(torch.load('mnist_cnn.pt', map_location='cpu', weights_only=True))
    model.eval()
    frozen = model.to_inference()
    print('\nFrozen FC1 weights (sample 4×8):')
    print(frozen['fc1']['W_int'][:4, :8])
    print(f"  FC1 scale: {frozen['fc1']['scale']:.6f}")
    print(f"\nFrozen FC2 weights (sample 4×8):")
    print(frozen['fc2']['W_int'][:4, :8])
    print(f"  FC2 scale: {frozen['fc2']['scale']:.6f}")
    print(f"\nUnique FC1 values: {frozen['fc1']['W_int'].unique().tolist()}  (should be -1,0,1)")
    print(f"Unique FC2 values: {frozen['fc2']['W_int'].unique().tolist()}  (should be -3..+3)")
    print("Step 1: Exporting weights...")
    fc1_W, fc1_s, fc2_W, fc2_s, norm1_g, norm2_g = export_weights(
        'mnist_cnn.pt', 'mnist_cnn_weights.npz')

    print("\nStep 2: Generating Verilog...")
    generate_verilog(fc1_W, fc2_W, norm1_g, norm2_g, "neuralnetwork.v")

    print_synthesis_notes(fc1_W, fc2_W)

# Generate Test-Cases
# Desc: Generate cocotb test-cases based on images from the MNIST test set.
# Inputs: None
# Returns: None
def generate_testcases():
    save_images = False

    # Load Data
    # ---------
    test_kwargs = {'batch_size': 64}
    transform = preprocessor()
    testdataset = datasets.MNIST('../data', train=False, transform=transform)
    test_loader = torch.utils.data.DataLoader(testdataset, **test_kwargs)

    # Save Preprocessed Images as dataframe
    # -------------------------------------
    print("Saving Test Images in batches: ")
    test_dataframe = pd.DataFrame(columns=["batch", "sample", "data vector", "label"])
    for batch_idx, (data, target) in enumerate(test_loader):
        print(str(batch_idx) + " ", end='')
        if(data.shape == (test_kwargs["batch_size"], 1, 14, 14)):
            for i, single_image in enumerate(data):
                flat_list = single_image.numpy().flatten(order='C').tolist()
                vector = ''.join(str(int(x)) for x in flat_list)
                row = {"batch":[batch_idx], "sample":[i], "data vector": [vector], "label":[int(target[i])]}
                new_row = pd.DataFrame(data=row)#,columns=["batch", "sample", "data vector", "label"])
                test_dataframe.reset_index(drop=True, inplace=True)
                new_row.reset_index(drop=True, inplace=True)
                test_dataframe = pd.concat([test_dataframe, new_row], ignore_index=True)
                if(save_images):
                    utils.save_image(single_image, '../data/MNIST/processed/test/batch{}_sample{}_class{}.png'.format(batch_idx, i, target[i]), normalize=False)

    # Generate Verilog Test Cases
    # ---------------------------
    print(test_dataframe.head())
    test_dataframe = test_dataframe.sample(n = 200)
    generate_cocotb_tests(test_dataframe, "randomtests.py")
    print("Cocotb testcases saved to randomtests.py")

if __name__ == '__main__':
    print("")
    print("Run from terminal without OSS CAD Suite enabled!")
    print("")
    print("MNIST Python Utility:")
    print("\t(1) Train Pytorch Model and save parameters")
    print("\t(2) Test Pytorch Model against MNIST testset")
    print("\t(3) Convert Pytorch Model to Verilog file neuralnetwork.v")
    print("\t(4) Generate cocotb testcases for Verilog testbench (test.py)")
    print("\t(5) Perform Benchmark - Run Pytorch and Tiny Tapeout chip in parallel (TBD)")

    selection = input("Enter an option (1-5): ")
    if(selection == '1'):
        print("Training Model...")
        model = train_model()
        print("Training Model...Done")
        print("Saving Model...")
        torch.save(model.state_dict(), "mnist_cnn.pt")
        print("Saving Model...Done")
    elif(selection == '2'):
        print("Loading Model...")
        model = Net()
        model.load_state_dict(torch.load('mnist_cnn.pt'))
        model.eval()
        #optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        print("Loading Model...Done")
        print("Testing Model...")
        test_model(model)
        print("Testing Model...Done")
    elif(selection == '3'):
        print("Loading Model")
        model = Net()
        model.load_state_dict(torch.load('mnist_cnn.pt'))
        model.eval()
        print("Loading Model...Done")
        print("Converting Model...")
        convert_model_to_verilog()
        print("Converting Model...Done")

    elif(selection == '4'):
        print("Generating Tests...")
        generate_testcases()
        print("Generating Tests...Done")
    else:
        print("Invalid Option...exiting.")
