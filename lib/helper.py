class Helper:
    BASE10_TO_HEX = dict(zip('0123456789abcdef', range(16)))

    def hex2rgb(hex_str):
        h = hex_str.strip().removeprefix('#').lower()
        if len(h) == 3:
            return [Helper.BASE10_TO_HEX[c]*17 for c in h]
        elif len(h) == 6:
            return [(Helper.BASE10_TO_HEX[a]*16) + Helper.BASE10_TO_HEX[b] for a,b in zip(h[::2],h[1::2])]
        else:
            raise ValueError(f'Invalid hex input {hex_str}')