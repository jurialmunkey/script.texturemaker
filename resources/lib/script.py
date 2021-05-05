# -*- coding: utf-8 -*-
# Module: default
# Author: jurialmunkey
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
import os
import sys
import xbmcaddon
import xbmcvfs
from PIL import Image

ADDON = xbmcaddon.Addon('script.texturemaker')
ADDONPATH = ADDON.getAddonInfo('path')
ADDONDATA = 'special://profile/addon_data/script.texturemaker/'

GRADIENT = xbmcvfs.translatePath('{}/resources/images/gradient.png'.format(ADDONPATH))


""" Usage
RunScript(script.texturemaker, fg=ffffffff, bg=ffffffff, alpha=1.0, folder=folder, mask_name=mask_file)

Output:
special://profile/addon_data/script.texturemaker/{folder}/{file}

gradient_h.png = Horizontal gradient from fg to bg with alpha applied to fg
gradient_v.png = gradient_h rotated 90 degrees
{mask_name}_h.png = gradient_h with {mask_file} applied as mask
{mask_name}_v.png = gradient_v with {mask_file} applied as mask

"""


def get_params():
    params = {}
    for arg in sys.argv:
        if arg == 'script.py':
            pass
        elif '=' in arg:
            arg_split = arg.split('=', 1)
            if arg_split[0] and arg_split[1]:
                key, value = arg_split
                params.setdefault(key, value)
        else:
            params.setdefault(arg, True)
    return params


def make_gradient(fg_color='#ffff00', bg_color='red', alpha=0.8, gradient=GRADIENT):
    # Open base image
    og_img = Image.open(gradient)

    # Apply alpha adjustment
    og_img.putalpha(og_img.getchannel('A').point(lambda x: x * alpha))

    # Apply colordiffuse
    fg_img = Image.new('RGBA', og_img.size, color=fg_color)
    fg_img.putalpha(og_img.getchannel('A'))

    # Layer over base color
    bg_img = Image.new('RGBA', og_img.size, color=bg_color)
    bg_img.paste(fg_img, (0, 0), fg_img)
    return bg_img


def make_masked(base, mask):
    mk_img = Image.open(mask)
    og_img = base.resize(mk_img.size)
    og_img.putalpha(mk_img.getchannel('A'))
    return og_img


class Script(object):
    def __init__(self):
        self.params = get_params()
        self.save_dir = '{}/{}'.format(ADDONDATA, self.params.get('folder', 'default'))
        self.fg_color = '#{}'.format(self.params.get('fg', 'ffffffff')[2:])
        self.bg_color = '#{}'.format(self.params.get('bg', 'ffffffff')[2:])
        self.alpha = float(self.params.get('alpha', 1.0))

    def make_gradients(self, fg_color, bg_color, alpha):
        self.gradient_h = make_gradient(fg_color, bg_color, alpha)
        self.gradient_h_file = xbmcvfs.translatePath('{}/gradient_h.png'.format(self.save_dir))
        self.gradient_h.save(self.gradient_h_file)

        self.gradient_v = self.gradient_h.rotate(90, expand=True)
        self.gradient_v_file = xbmcvfs.translatePath('{}/gradient_v.png'.format(self.save_dir))
        self.gradient_v.save(self.gradient_v_file)

    def run(self):
        if not os.path.exists(xbmcvfs.translatePath(self.save_dir)):
            os.makedirs(xbmcvfs.translatePath(self.save_dir))

        self.make_gradients(self.fg_color, self.bg_color, self.alpha)

        for k, v in self.params.items():
            if k in ['fg', 'bg', 'alpha', 'folder']:
                continue

            mask = xbmcvfs.translatePath(v)
            mask_h_file = xbmcvfs.translatePath('{}/{}_h.png'.format(self.save_dir, k))
            mask_v_file = xbmcvfs.translatePath('{}/{}_v.png'.format(self.save_dir, k))
            make_masked(self.gradient_h, mask).save(mask_h_file)
            make_masked(self.gradient_v, mask).save(mask_v_file)
