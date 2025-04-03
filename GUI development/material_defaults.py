import json
import os

class MaterialDefaults:
    def __init__(self):
        self.defaults_file = "material_defaults.json"
        self.materials = self.load_defaults()
    
    def load_defaults(self):
        if os.path.exists(self.defaults_file):
            with open(self.defaults_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_defaults(self):
        with open(self.defaults_file, 'w') as f:
            json.dump(self.materials, f, indent=4)
    
    def add_material(self, name, values):
        self.materials[name] = values
        self.save_defaults()
    
    def get_material_values(self, material):
        return self.materials.get(material, {})
    
    def get_materials_list(self):
        return list(self.materials.keys())
