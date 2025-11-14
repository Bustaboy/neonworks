"""
Style Transfer System for Sprites

Transfer artistic styles between sprites or apply reference art styles
to game sprites. Supports both AI-powered and traditional methods.

Features:
- Neural style transfer for artistic effects
- Palette swapping for quick color style changes
- Texture transfer for material effects
- Multi-sprite batch processing
- Style mixing and blending

Hardware Requirements:
- GPU recommended but not required
- NVIDIA (CUDA), AMD (ROCm), or CPU
- 4+ GB VRAM for AI methods, any for traditional

Author: NeonWorks Team
License: MIT
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import json

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
from PIL import Image
import torchvision.transforms as transforms
import torchvision.models as models


@dataclass
class StyleTransferConfig:
    """Configuration for style transfer."""

    content_image: Image.Image
    style_image: Image.Image
    output_size: Tuple[int, int] = (512, 512)

    # Neural style transfer settings
    num_steps: int = 300
    style_weight: float = 1000000
    content_weight: float = 1
    learning_rate: float = 0.01

    # Style layers and weights
    style_layers: List[str] = None
    content_layers: List[str] = None

    # Traditional methods
    method: str = "neural"  # neural, palette, texture
    preserve_alpha: bool = True

    # Palette swapping
    num_colors: int = 16
    dithering: bool = False

    def __post_init__(self):
        """Initialize default layer configurations."""
        if self.style_layers is None:
            self.style_layers = [
                'conv1_1', 'conv2_1', 'conv3_1', 'conv4_1', 'conv5_1'
            ]

        if self.content_layers is None:
            self.content_layers = ['conv4_2']


class VGGFeatures(nn.Module):
    """
    VGG19 feature extractor for neural style transfer.

    Extracts features from specific layers for style and content
    representation.
    """

    def __init__(self, device: str = "cuda"):
        """Initialize VGG feature extractor."""
        super().__init__()
        self.device = device

        # Load pre-trained VGG19
        vgg = models.vgg19(pretrained=True).features.to(device).eval()

        # Disable gradients
        for param in vgg.parameters():
            param.requires_grad_(False)

        self.model = vgg

        # Layer name mapping
        self.layer_names = {
            '0': 'conv1_1', '2': 'conv1_2',
            '5': 'conv2_1', '7': 'conv2_2',
            '10': 'conv3_1', '12': 'conv3_2', '14': 'conv3_3', '16': 'conv3_4',
            '19': 'conv4_1', '21': 'conv4_2', '23': 'conv4_3', '25': 'conv4_4',
            '28': 'conv5_1', '30': 'conv5_2', '32': 'conv5_3', '34': 'conv5_4',
        }

        # Normalization for ImageNet
        self.mean = torch.tensor([0.485, 0.456, 0.406]).to(device).view(-1, 1, 1)
        self.std = torch.tensor([0.229, 0.224, 0.225]).to(device).view(-1, 1, 1)

    def forward(self, x: torch.Tensor, layers: List[str]) -> Dict[str, torch.Tensor]:
        """
        Extract features from specified layers.

        Args:
            x: Input tensor (B, C, H, W)
            layers: List of layer names to extract

        Returns:
            Dictionary mapping layer names to feature tensors
        """
        # Normalize input
        x = (x - self.mean) / self.std

        features = {}
        for name, layer in self.model._modules.items():
            x = layer(x)
            layer_name = self.layer_names.get(name)
            if layer_name in layers:
                features[layer_name] = x

        return features


def gram_matrix(tensor: torch.Tensor) -> torch.Tensor:
    """
    Compute Gram matrix for style representation.

    Args:
        tensor: Feature tensor (B, C, H, W)

    Returns:
        Gram matrix (B, C, C)
    """
    b, c, h, w = tensor.size()
    features = tensor.view(b, c, h * w)
    gram = torch.bmm(features, features.transpose(1, 2))
    return gram / (c * h * w)


def content_loss(content_features: torch.Tensor, target_features: torch.Tensor) -> torch.Tensor:
    """Compute content loss (MSE)."""
    return F.mse_loss(content_features, target_features)


def style_loss(style_features: torch.Tensor, target_features: torch.Tensor) -> torch.Tensor:
    """Compute style loss (Gram matrix MSE)."""
    style_gram = gram_matrix(style_features)
    target_gram = gram_matrix(target_features)
    return F.mse_loss(style_gram, target_gram)


class NeuralStyleTransfer:
    """
    Neural style transfer using VGG19 features.

    Transfers artistic style from a reference image to a content image
    using deep neural network features.
    """

    def __init__(self, device: Optional[str] = None):
        """Initialize neural style transfer."""
        self.device = device or self._detect_device()
        self.feature_extractor = VGGFeatures(device=self.device)
        print(f"Neural Style Transfer initialized on {self.device}")

    def _detect_device(self) -> str:
        """Detect best available device."""
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0).lower()
            if 'amd' in device_name or 'radeon' in device_name:
                print(f"Detected AMD GPU (ROCm): {torch.cuda.get_device_name(0)}")
            else:
                print(f"Detected NVIDIA GPU: {torch.cuda.get_device_name(0)}")
            return "cuda"
        elif torch.backends.mps.is_available():
            print("Detected Apple Silicon GPU (MPS)")
            return "mps"
        else:
            print("No GPU detected, using CPU")
            return "cpu"

    def _image_to_tensor(self, image: Image.Image, size: Tuple[int, int]) -> torch.Tensor:
        """Convert PIL Image to tensor."""
        transform = transforms.Compose([
            transforms.Resize(size),
            transforms.ToTensor(),
        ])
        return transform(image).unsqueeze(0).to(self.device)

    def _tensor_to_image(self, tensor: torch.Tensor) -> Image.Image:
        """Convert tensor to PIL Image."""
        tensor = tensor.cpu().clone().squeeze(0)
        tensor = tensor.clamp(0, 1)
        transform = transforms.ToPILImage()
        return transform(tensor)

    def transfer(self, config: StyleTransferConfig) -> Image.Image:
        """
        Perform neural style transfer.

        Args:
            config: Style transfer configuration

        Returns:
            Stylized image
        """
        print("Starting neural style transfer...")

        # Convert images to tensors
        content = self._image_to_tensor(config.content_image, config.output_size)
        style = self._image_to_tensor(config.style_image, config.output_size)

        # Initialize output with content image
        output = content.clone().requires_grad_(True)

        # Extract target features
        with torch.no_grad():
            content_features = self.feature_extractor(content, config.content_layers)
            style_features = self.feature_extractor(style, config.style_layers)

        # Optimizer
        optimizer = optim.Adam([output], lr=config.learning_rate)

        # Optimization loop
        print(f"Optimizing for {config.num_steps} steps...")
        for step in range(config.num_steps):
            optimizer.zero_grad()

            # Extract features from current output
            output_content_features = self.feature_extractor(output, config.content_layers)
            output_style_features = self.feature_extractor(output, config.style_layers)

            # Compute losses
            c_loss = 0
            for layer in config.content_layers:
                c_loss += content_loss(
                    output_content_features[layer],
                    content_features[layer]
                )

            s_loss = 0
            for layer in config.style_layers:
                s_loss += style_loss(
                    output_style_features[layer],
                    style_features[layer]
                )

            # Total loss
            total_loss = (
                config.content_weight * c_loss +
                config.style_weight * s_loss
            )

            # Backprop and update
            total_loss.backward()
            optimizer.step()

            # Clamp to valid range
            with torch.no_grad():
                output.clamp_(0, 1)

            # Progress
            if (step + 1) % 50 == 0 or step == 0:
                print(f"Step {step+1}/{config.num_steps}: "
                      f"Content Loss: {c_loss.item():.4f}, "
                      f"Style Loss: {s_loss.item():.4f}")

        # Convert back to image
        result = self._tensor_to_image(output)

        # Preserve alpha channel if needed
        if config.preserve_alpha and config.content_image.mode == "RGBA":
            result = result.convert("RGBA")
            result.putalpha(config.content_image.split()[3])

        print("Style transfer complete!")
        return result


class PaletteSwapper:
    """
    Palette-based style transfer.

    Extracts color palette from style image and applies it to content
    image. Fast, deterministic, preserves details.
    """

    def __init__(self):
        """Initialize palette swapper."""
        pass

    def extract_palette(
        self,
        image: Image.Image,
        num_colors: int = 16
    ) -> List[Tuple[int, int, int]]:
        """
        Extract color palette from image.

        Args:
            image: Source image
            num_colors: Number of colors in palette

        Returns:
            List of RGB tuples
        """
        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Quantize to reduce colors
        quantized = image.quantize(colors=num_colors, method=2)
        palette = quantized.getpalette()

        # Extract RGB colors
        colors = []
        for i in range(num_colors):
            r = palette[i * 3]
            g = palette[i * 3 + 1]
            b = palette[i * 3 + 2]
            colors.append((r, g, b))

        return colors

    def apply_palette(
        self,
        image: Image.Image,
        palette: List[Tuple[int, int, int]],
        dithering: bool = False
    ) -> Image.Image:
        """
        Apply palette to image.

        Args:
            image: Image to recolor
            palette: Target color palette
            dithering: Enable dithering for smoother transitions

        Returns:
            Recolored image
        """
        # Convert to RGB
        original_mode = image.mode
        alpha = None
        if image.mode == "RGBA":
            alpha = image.split()[3]
            image = image.convert("RGB")
        elif image.mode != "RGB":
            image = image.convert("RGB")

        # Create palette image
        num_colors = len(palette)
        palette_img = Image.new("P", (1, 1))
        flat_palette = []
        for color in palette:
            flat_palette.extend(color)
        # Pad to 256 colors
        while len(flat_palette) < 768:
            flat_palette.append(0)
        palette_img.putpalette(flat_palette)

        # Quantize image to palette
        dither = Image.FLOYDSTEINBERG if dithering else Image.NONE
        result = image.quantize(palette=palette_img, dither=dither)
        result = result.convert("RGB")

        # Restore alpha
        if alpha:
            result = result.convert("RGBA")
            result.putalpha(alpha)

        return result

    def transfer_palette(
        self,
        content: Image.Image,
        style: Image.Image,
        num_colors: int = 16,
        dithering: bool = False
    ) -> Image.Image:
        """
        Transfer palette from style to content.

        Args:
            content: Image to recolor
            style: Source of palette
            num_colors: Palette size
            dithering: Enable dithering

        Returns:
            Recolored image
        """
        print(f"Extracting {num_colors} color palette from style image...")
        palette = self.extract_palette(style, num_colors)

        print("Applying palette to content image...")
        result = self.apply_palette(content, palette, dithering)

        print("Palette transfer complete!")
        return result


class StyleTransferSystem:
    """
    Unified style transfer system.

    Combines multiple style transfer methods with intelligent selection
    based on input and hardware.
    """

    def __init__(self, prefer_gpu: bool = True):
        """Initialize style transfer system."""
        self.prefer_gpu = prefer_gpu
        self.neural_transfer = None
        self.palette_swapper = PaletteSwapper()

        # Try to initialize neural transfer
        if prefer_gpu:
            try:
                self.neural_transfer = NeuralStyleTransfer()
            except Exception as e:
                print(f"Could not initialize neural transfer: {e}")
                print("Will use traditional methods only")

    def transfer(
        self,
        content: Image.Image,
        style: Image.Image,
        method: str = "auto",
        **kwargs
    ) -> Image.Image:
        """
        Transfer style from style image to content image.

        Args:
            content: Image to stylize
            style: Style reference image
            method: Method to use (auto, neural, palette)
            **kwargs: Method-specific parameters

        Returns:
            Stylized image
        """
        # Auto-select method
        if method == "auto":
            if self.neural_transfer is not None:
                # Use neural for larger images or complex styles
                if max(content.size) > 256:
                    method = "neural"
                else:
                    method = "palette"
            else:
                method = "palette"

        print(f"Using {method} style transfer method")

        # Perform transfer
        if method == "neural":
            if self.neural_transfer is None:
                raise ValueError("Neural transfer not available (GPU required)")

            config = StyleTransferConfig(
                content_image=content,
                style_image=style,
                **kwargs
            )
            return self.neural_transfer.transfer(config)

        elif method == "palette":
            num_colors = kwargs.get("num_colors", 16)
            dithering = kwargs.get("dithering", False)
            return self.palette_swapper.transfer_palette(
                content, style, num_colors, dithering
            )

        else:
            raise ValueError(f"Unknown method: {method}")

    def batch_transfer(
        self,
        content_images: List[Image.Image],
        style: Image.Image,
        method: str = "auto",
        output_dir: Optional[Path] = None,
        **kwargs
    ) -> List[Image.Image]:
        """
        Apply style transfer to multiple images.

        Args:
            content_images: List of images to stylize
            style: Style reference
            method: Transfer method
            output_dir: Directory to save results (optional)
            **kwargs: Method-specific parameters

        Returns:
            List of stylized images
        """
        results = []

        for i, content in enumerate(content_images):
            print(f"\nProcessing image {i+1}/{len(content_images)}")
            result = self.transfer(content, style, method, **kwargs)
            results.append(result)

            if output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                result.save(output_dir / f"styled_{i:03d}.png")

        return results


# Convenience function

def transfer_style(
    content: Image.Image | str | Path,
    style: Image.Image | str | Path,
    method: str = "auto",
    output_path: Optional[str | Path] = None,
    **kwargs
) -> Image.Image:
    """
    Quick style transfer function.

    Args:
        content: Content image or path
        style: Style image or path
        method: Transfer method (auto, neural, palette)
        output_path: Path to save result (optional)
        **kwargs: Method-specific parameters

    Returns:
        Stylized image

    Example:
        >>> result = transfer_style(
        ...     "character.png",
        ...     "art_style.png",
        ...     method="palette",
        ...     num_colors=16
        ... )
    """
    # Load images if paths
    if isinstance(content, (str, Path)):
        content = Image.open(content)
    if isinstance(style, (str, Path)):
        style = Image.open(style)

    # Create system and transfer
    system = StyleTransferSystem()
    result = system.transfer(content, style, method, **kwargs)

    # Save if requested
    if output_path:
        result.save(output_path)
        print(f"Saved to {output_path}")

    return result


if __name__ == "__main__":
    print("Style Transfer System - Example Usage\n")

    # Create some test images
    content = Image.new("RGB", (256, 256), color=(100, 150, 200))
    style = Image.new("RGB", (256, 256), color=(200, 100, 50))

    # Palette transfer (fast, works on any hardware)
    print("Testing palette transfer...")
    system = StyleTransferSystem(prefer_gpu=False)
    result = system.transfer(content, style, method="palette", num_colors=8)
    result.save("test_palette_transfer.png")

    print("\nExample complete!")
