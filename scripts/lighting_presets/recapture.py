# -*- coding: utf-8 -*-
"""값은 그대로 두고 대표 구도만 다시 찍는다(게임 뷰 유지 확인 포함)."""
import sys
from ue_mcp import UE
from cameras import PRESETS
import apply as ap, shoot, gameview, hide_sprites
TAG = {"BlueHour": "bh", "GoldenHour": "gh", "Night": "nt"}

def main(argv):
    u = UE()
    args = [a for a in argv if not a.startswith("--")]
    for name in (args or PRESETS):
        ap.load(u, name)
        hide_sprites.run(u, verbose=False)
        gameview.ensure(u, shoot.CAMERAS[2])
        print(name, shoot.shoot(u, "final_" + TAG[name])[0])


if __name__ == "__main__":
    main(sys.argv[1:])
