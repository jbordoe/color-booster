import numpy as np

class Booster:
    @staticmethod
    def boost(lab_im, lab_color,
        Dd=300,  # Distance denominator (default ~= max L*a*b dist)
        sigL=1,  # Sigmoid max value
        sigk=10,  # Sigmoid steepness
        sigx0=0.8, # Sigmoid midpoint
    ):
        D, V = Booster._distance_vectors(lab_im, lab_color)
        D = 1 - D/Dd
        D = sigL / (1 + np.exp(-((D-sigx0)*sigk)))
    
        # Scale vector by (modified) distance to colour
        V *= D.reshape((D.shape[0], D.shape[1], 1))
        return lab_im + V, D, V
    
    @staticmethod
    def boost_multi(lab_im, configs, ordered=False):
        boosted_im = np.copy(lab_im)
        if len(configs) == 0: return boosted_im
        for config in configs:
            if ordered:
                boosted_im, _D, _V = Booster.boost(
                    boosted_im,
                    config['color'],
                    sigL=config['sigL'],
                    sigk=config['sigk'],
                    sigx0=config['sigx0']
                )
            else:
                _mod_im, D, V = Booster.boost(
                    lab_im,
                    config['color'],
                    sigL=config['sigL'],
                    sigk=config['sigk'],
                    sigx0=config['sigx0']
                )
                boosted_im = boosted_im + V
        return boosted_im

    @staticmethod
    def _distance_vectors(im, c):
        X = im.astype(float)
        C = np.ones(im.shape, np.float32) * c
        V = C - X
        D = np.square(V).sum(axis=2)**.5

        return D, V