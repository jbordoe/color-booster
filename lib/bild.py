import numpy as np
import cv2
import io
import PIL.Image

class Bild:
    def __init__(self, im):
        if (np.max(im) <= 1 and np.min(im) >= 0):
            im = im * 255
        self._rgb = im
        pass
    
    def from_file(path):
        bgr_im = cv2.imread(path, cv2.IMREAD_COLOR)
        rgb_im = cv2.cvtColor(bgr_im, cv2.COLOR_BGR2RGB)
        return Bild(rgb_im)
    
    def from_bytes(bytestr):
        np_im = np.asarray(bytearray(bytestr), dtype=np.uint8)
        bgr_im = cv2.imdecode(np_im, flags=1)
        rgb_im = cv2.cvtColor(bgr_im, cv2.COLOR_BGR2RGB)
        return Bild(rgb_im)

    def lab(self):
        return cv2.cvtColor(self._rgb, cv2.COLOR_RGB2LAB).astype(float)
    
    def rgb(self, normalize=False):
        return self._rgb / 255 if normalize else self._rgb
    
    def bgr(self):
        return self.cv2.cvtColor(self._rgb, cv2.COLOR_RGB2BGR)
    
    def resize(self, h=None, w=None, keep_ratio=False, inplace=False):
        if (not h and not w):
            raise ValueError("Invalid parameters")
        else:
            if keep_ratio:
                factor = (h/self._rgb.shape[0]) if h else (w/self._rgb.shape[1])
                return self.scale(factor, inplace=inplace)
            else:
                w = w or self._rgb.shape[0]
                h = h or self._rgb.shape[1]
                rgb = cv2.resize(self._rgb, (w,h))
                if inplace:
                    self._rgb = rgb
                else:
                    return Bild(rgb)
        
    def scale(self, factor, inplace=False):
        return self.resize(
            h=int(self._rgb.shape[0] * factor),
            w=int(self._rgb.shape[1] * factor),
            inplace=inplace
        )
    
    def concat(self, im, inplace=False):
        res = np.concatenate((self._rgb, im.rgb()), axis=1)
        if inplace:
            self._rgb = res
        else:
            return Bild(res)
    
    def to_bytes(self, fmt):
        buff = io.BytesIO()
        img = PIL.Image.fromarray(self._rgb)    
        img.save(buff, format=fmt)

        return buff.getvalue()