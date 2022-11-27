import base64
import cv2
import ipywidgets as widgets
from IPython.display import display, Javascript
import json
import numpy as np

from lib.bild import Bild
from lib.booster import Booster
from lib.helper import Helper
from lib.layer import Layer

class App:
    class NullDisplay:
        def __init__(self): pass
        def refresh(self): pass
        def refresh_image(self): pass

    def __init__(self):
        self.state = 'idle'
        self.layers = []
        self.ordered = False
        self.image = None
        self.output_image = None
        self.display = App.NullDisplay()
        self.preview = None
        self.widgets = {
            'add_layer': widgets.Button(
                description="Add A Layer",
                button_style="primary",
                icon="fa-plus",
                disabled=True,
            ),
            'save_layers': widgets.Button(
                description="Save Layers",
                button_style="info",
                icon="fa-save",
                disabled=True,
            ),
            'upload_layers': widgets.FileUpload(
                accept='application/json',
                description="Load Layers",
                button_style="info",
                tooltip="Open layer file",
                disabled=True,
                multiple=False,
            ),
            'upload_image': widgets.FileUpload(
                accept='image/*',
                description="Upload Image",
                button_style="primary",
                tooltip="Upload an image to edit",
                disabled=False,
                multiple=False,
            ),
            'save_image': widgets.Button(
                description="Save Result",
                button_style="success",
                disabled=True,
                icon="fa-check",
            ),
            'ordered': widgets.Checkbox(
                value=False,
                description='Order layers (recalcuate at each step)',
                disabled=True,
                indent=False
            ),
            'output': widgets.Output()
        }
        self.widgets['add_layer'].on_click(self.add_layer)
        self.widgets['save_layers'].on_click(self.save_layers)
        self.widgets['save_image'].on_click(self.save_image)
        self.widgets['upload_image'].observe(self.upload_image)
        self.widgets['upload_layers'].observe(self.load_layers)
        self.widgets['ordered'].observe(self.refresh_image)
    
    def refresh(self, _=None):
        pass

    def refresh_image(self, _=None):
        if not self.image: return

        configs = [l.booster_config() for l in self.layers if l.enabled]
        lab_im = self.preview.lab()
        boosted_lab = Booster.boost_multi(
            lab_im,
            configs,
            ordered=self.widgets['ordered'].value
        )
        boosted_lab = np.uint8(boosted_lab.astype(int))
        boosted_im = Bild(cv2.cvtColor(boosted_lab, cv2.COLOR_LAB2RGB))
        self.output_image = boosted_im
        self.display.refresh_image()

    def add_layer(self, _btn, config={}):
        layer = Layer(self, config)
        self.layers.append(layer)
        self.display.refresh()

    def delete_layer(self, layer):
        self.layers = [l for l in self.layers if l != layer]
        self.display.refresh()

    def upload_image(self, change):
        if len(change.owner.value):
            bytestr = change.owner.value[0].content.tobytes()
            im = Bild.from_bytes(bytestr)
            preview_im = im.resize(w=300, keep_ratio=True)
            self.image = im
            self.preview = preview_im
            self.output_image = preview_im

            self.enable_buttons()
            self.display.refresh_image()

    def save_image(self, _btn):
        self.disable_buttons()
        configs = [l.booster_config() for l in self.layers if l.enabled]
        lab_im = self.image.lab()
        boosted_lab = Booster.boost_multi(
            lab_im,
            configs,
            ordered=self.widgets['ordered'].value
        )
        boosted_lab = np.uint8(boosted_lab.astype(int))
        boosted_im = Bild(cv2.cvtColor(boosted_lab, cv2.COLOR_LAB2RGB))
        im_bytes = boosted_im.to_bytes('png')
        b64_bytes = base64.b64encode(im_bytes)
        b64_str = b64_bytes.decode('ascii')
        js_code = """
            var a = document.createElement("a");
            a.href = "data:%s;base64,%s";
            a.download = 'result.png';
            a.click();
            a.remove();
        """
        with self.widgets['output']:
            js = Javascript(js_code % ("image/png", b64_str))
            display(js)
            self.widgets['output'].clear_output()
            self.enable_buttons()

    def save_layers(self, _btn):
        layer_configs = []
        for layer in self.layers:
            config = layer.booster_config()
            del config["color"]
            layer_configs.append(config)

        data = {
            'layers': layer_configs,
            'ordered': self.ordered,
        }
        message_bytes = json.dumps(data).encode('ascii')
        b64_str = base64.b64encode(message_bytes).decode('ascii')

        js_code = """
            var a = document.createElement("a");
            a.href = "data:%s;base64,%s"
            a.download = "booster_layers.json";
            a.click();
            a.remove()
        """
        with self.widgets['output']:
            js = Javascript(js_code % ("application/json", b64_str))
            display(js)
            self.widgets['output'].clear_output()
            
    def load_layers(self, change):
        if len(change.owner.value):
            bytestr = change.owner.value[0].content.tobytes()
            layers_json = bytestr.decode('utf8')
            config = json.loads(layers_json)
            self.layers = [Layer(self, c) for c in config['layers']]
            self.ordered = config.get('ordered', False)
            self.display.refresh()
    
    def disable_buttons(self):
        for w in self.widgets.values(): w.disabled = True
            
    def enable_buttons(self):
        for w in self.widgets.values(): w.disabled = False
