import base64
import cv2
import json

import ipywidgets as widgets
from IPython.display import display, Javascript

from lib.app import App
from lib.bild import Bild
from lib.helper import Helper
from lib.layer import Layer

class AppWidget:
    def __init__(self, app):
        self.app = app
        app.display = self
        self.input_image = None
        self.image = widgets.HTML(value="<h3>Upload an Image!</h3>")
    
    def display(self):
        display(self.app.widgets['output'])

        self.controls = widgets.VBox([
            widgets.HTML("<h2>Colour Booster</h2>"),
            widgets.HBox([
                self.app.widgets['upload_image'],
                self.app.widgets['add_layer'],
                self.app.widgets['upload_layers'],
                self.app.widgets['save_layers'],
                self.app.widgets['save_image'],
            ]),
            self.app.widgets['ordered'],
        ])

        self.layout = widgets.AppLayout(
            header=self.controls,
            left_sidebar=self.layers(),
            center=None,
            right_sidebar=self.image,
            footer=None
        )
        display(self.layout)
        
    def layers(self):
        layers = []
        titles = []
        for layer in self.app.layers:
            box = widgets.VBox([
                layer.widgets['toggle'],
                layer.widgets['color'],
                layer.widgets['sigx0'],
                layer.widgets['sigk'],
                layer.widgets['sigL'],
                widgets.HBox([
                    layer.widgets['reset'],
                    layer.widgets['destroy']
                ])
            ])
            layers.append(box)
            titles.append(layer.widgets['color'].value)
        return widgets.Accordion(children=layers, titles=titles)
    
    def refresh(self):
        self.layout.left_sidebar = self.layers()
        self.refresh_image()
        
    def refresh_image(self):
        if self.app.image:
            if not self.input_image:
                self.image = widgets.Image(format='png')
                self.layout.right_sidebar = self.image
            self.input_image = self.app.preview
            output_image = self.app.output_image
            self.image.value = self.input_image.concat(output_image).to_bytes('png')
        else:
            self.image = widgets.HTML(value="<h3>Upload an Image!</h3>")
