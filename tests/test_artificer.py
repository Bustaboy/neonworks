from __future__ import annotations

import json

from neonworks.agents.artificer import Artificer


def test_build_asset_index_finds_png_and_ogg(tmp_path):
    assets_root = tmp_path / "assets"
    assets_root.mkdir()

    img1 = assets_root / "sprite.png"
    img2 = assets_root / "ui" / "button.png"
    snd1 = assets_root / "audio" / "click.ogg"
    other = assets_root / "notes.txt"

    img2.parent.mkdir(parents=True, exist_ok=True)
    snd1.parent.mkdir(parents=True, exist_ok=True)

    img1.write_bytes(b"\x89PNG\r\n\x1a\n")
    img2.write_bytes(b"\x89PNG\r\n\x1a\n")
    snd1.write_bytes(b"OggS")
    other.write_text("not an asset", encoding="utf-8")

    artificer = Artificer()
    index = artificer.build_asset_index(assets_root)

    assert isinstance(index, dict)
    assert index["root"] == str(assets_root.resolve())
    assets = index["assets"]
    assert isinstance(assets, list)

    paths = {a["path"] for a in assets}
    assert paths == {"sprite.png", "ui/button.png", "audio/click.ogg"}

    for entry in assets:
        assert set(entry.keys()) == {"filename", "path", "tags"}
        assert isinstance(entry["filename"], str)
        assert isinstance(entry["path"], str)
        assert isinstance(entry["tags"], list)


def test_save_and_load_asset_index_round_trip(tmp_path):
    assets_root = tmp_path / "assets"
    assets_root.mkdir()
    (assets_root / "sprite.png").write_bytes(b"\x89PNG\r\n\x1a\n")

    artificer = Artificer()
    index = artificer.build_asset_index(assets_root)

    index_path = tmp_path / "asset_index.json"
    artificer.save_asset_index(index, index_path)

    assert index_path.is_file()

    loaded = artificer.load_asset_index(index_path)
    assert loaded == index

    with index_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    assert set(raw.keys()) == {"root", "assets"}


def test_load_asset_index_missing_file_returns_empty(tmp_path):
    artificer = Artificer()
    missing_path = tmp_path / "no_index.json"
    assert not missing_path.exists()

    loaded = artificer.load_asset_index(missing_path)
    assert loaded == {"root": "", "assets": []}

