"""
This source code is based on vits.py, which is licensed under the Attribution-NonCommercial 4.0 International License.
Original source code: https://github.com/facebookresearch/moco-v3/blob/main/vits.py
"""


import math
import torch
import torch.nn as nn
from functools import partial, reduce
from operator import mul

from lib.models.vision_transformer import VisionTransformer, _cfg # from timm.models.vision_transformer import VisionTransformer, _cfg
from lib.layers.patch_embed import PatchEmbedABC, PatchEmbed3D, ConvStem3D
from lib.layers.position_embed import build_3d_sincos_position_embedding

__all__ = [
    'vit_3d_small', 
    'vit_3d_base',
    'vit_3d_conv_small',
    'vit_3d_conv_base',
    'vit_3d_base_patchsize8',
    'VisionTransformerMoCo3D',
]

class VisionTransformerMoCo3D(VisionTransformer):
    def __init__(self, stop_grad_conv1=False, **kwargs):
        super().__init__(**kwargs)
        # Use fixed 3D sin-cos position embedding
        self.pos_embed = build_3d_sincos_position_embedding(grid_size=self.patch_embed.grid_size, embed_dim=self.embed_dim, num_tokens=self.num_prefix_tokens)

        # weight initialization
        self.init_weights(mode="moco")

        if isinstance(self.patch_embed, PatchEmbedABC):
            # xavier_uniform initialization
            val = math.sqrt(6. / float(3 * reduce(mul, self.patch_embed.patch_size, 1) + self.embed_dim))
            nn.init.uniform_(self.patch_embed.proj.weight, -val, val)
            nn.init.zeros_(self.patch_embed.proj.bias)

            if stop_grad_conv1:
                self.patch_embed.proj.weight.requires_grad = False
                self.patch_embed.proj.bias.requires_grad = False


def vit_3d_small(**kwargs):
    model = VisionTransformerMoCo3D(
        patch_size=16, embed_dim=384, depth=12, num_heads=12, mlp_ratio=4, qkv_bias=True,
        norm_layer=partial(nn.LayerNorm, eps=1e-6), embed_layer=PatchEmbed3D, **kwargs)
    model.default_cfg = _cfg()
    return model

def vit_3d_base(**kwargs):
    model = VisionTransformerMoCo3D(
        patch_size=16, embed_dim=768, depth=12, num_heads=12, mlp_ratio=4, qkv_bias=True,
        norm_layer=partial(nn.LayerNorm, eps=1e-6), embed_layer=PatchEmbed3D, **kwargs)
    model.default_cfg = _cfg()
    return model

def vit_3d_conv_small(**kwargs):
    # minus one ViT block
    model = VisionTransformerMoCo3D(
        patch_size=16, embed_dim=384, depth=11, num_heads=12, mlp_ratio=4, qkv_bias=True,
        norm_layer=partial(nn.LayerNorm, eps=1e-6), embed_layer=ConvStem3D, **kwargs)
    model.default_cfg = _cfg()
    return model

def vit_3d_conv_base(**kwargs):
    # minus one ViT block
    model = VisionTransformerMoCo3D(
        patch_size=16, embed_dim=768, depth=11, num_heads=12, mlp_ratio=4, qkv_bias=True,
        norm_layer=partial(nn.LayerNorm, eps=1e-6), embed_layer=ConvStem3D, **kwargs)
    model.default_cfg = _cfg()
    return model

def vit_3d_base_patchsize8(**kwargs):
    model = VisionTransformerMoCo3D(
        patch_size=8, embed_dim=768, depth=12, num_heads=12, mlp_ratio=4, qkv_bias=True,
        norm_layer=partial(nn.LayerNorm, eps=1e-6), embed_layer=PatchEmbed3D, **kwargs)
    model.default_cfg = _cfg()
    return model