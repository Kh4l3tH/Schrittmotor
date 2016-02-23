class Koordinatensystem():
    def __init__(self, config, ks):
        self.name = ks
        self.x_offset = config.getfloat(ks, 'x_offset')
        self.x_inverted = config.getboolean(ks, 'x_inverted')
        self.z_offset = config.getfloat(ks, 'z_offset')
        self.z_inverted = config.getboolean(ks, 'z_inverted')
