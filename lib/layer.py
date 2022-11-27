import cv2
import numpy as np

from lib.helper import Helper
import ipywidgets as widgets

class Layer:
    def __init__(self, parent, config={}):
        self.parent = parent
        self.enabled = config.get('enabled', True)
        self.widgets = {
            'color': widgets.ColorPicker(
                concise=False,
                description='Pick a color',
                value=config.get('hexColor', '#ff2211'),
                disabled=False,
            ), 
            'sigx0': widgets.FloatSlider(
                value=config.get('sigx0', 0.8),
                min=0,
                max=1,
                step=0.05,
                description='x0 (sigmoid midpoint):',
                disabled=False,
                continuous_update=True,
                orientation='horizontal',
                readout=True,
                readout_format='.1f',
            ),
            'sigk': widgets.IntSlider(
                value=config.get('sigk', 15),
                min=0,
                max=100,
                step=1,
                description='k: (sigmoid steepness)',
                disabled=False,
                continuous_update=True,
                orientation='horizontal',
                readout=True,
            ),
            'sigL': widgets.FloatSlider(
                value=config.get('sigL', 1),
                min=0,
                max=1,
                step=0.05,
                description='L (sigmoid maximum):',
                disabled=False,
                continuous_update=True,
                orientation='horizontal',
                readout=True,
                readout_format='.1f',
            ),
            'reset': widgets.Button(description="Reset", icon="fa-refresh"),
            'destroy': widgets.Button(
                description="Remove",
                button_style='danger',
                icon="fa-trash-o",
            ),
            'toggle': widgets.Button(
                description='Enabled',
                button_style='success',
                tooltip='Click to toggle',
                icon='toggle-on'
            )
        }
        self.widgets['reset'].on_click(self.reset)
        self.widgets['destroy'].on_click(self.destroy)
        self.widgets['toggle'].on_click(self.toggle)
        
        for w in ["sigx0", "sigk", "sigL", "color", "toggle"]:
            self.widgets[w].observe(self.parent.refresh_image)
            
    def toggle(self, btn):
        self.enabled = not self.enabled
        if self.enabled:
            btn.description = 'Enabled'
            btn.button_style = 'success'
            btn.icon = 'toggle-on'
        else:
            btn.description = 'Disabled'
            btn.button_style = 'warning'
            btn.icon = 'toggle-off'

        for w in ["sigx0", "sigk", "sigL", "color", "reset"]:
            self.widgets[w].disabled = not self.enabled
            
    
    def reset(self, _b):
        self.widgets['sigx0'].value = 0.8
        self.widgets['sigk'].value = 15
        self.widgets['sigL'].value = 1
        
    def destroy(self, _b):
        self.parent.delete_layer(self)

    def booster_config(self):
        rgb_color = np.array([[Helper.hex2rgb(self.widgets['color'].value)]], np.uint8)
        lab_color = cv2.cvtColor(rgb_color, cv2.COLOR_RGB2LAB)
    
        config = {
            'hexColor': self.widgets['color'].value,
            'color': lab_color,
            'sigx0': self.widgets['sigx0'].value,
            'sigk': self.widgets['sigk'].value,
            'sigL': self.widgets['sigL'].value,
            'enabled': self.enabled,
        }
        return config