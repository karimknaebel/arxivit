import pytest
from PIL import Image

from arxivit import parse_image_options, process_image


@pytest.mark.parametrize("size_option,expected_size", [("", 32), (",16px", 16)])
@pytest.mark.parametrize("format_option,expected_format", [("", "PNG"), ("jpeg,", "JPEG")])
@pytest.mark.parametrize(
    "background_color,alpha,expected_color",
    [
        ("white", 0, (255, 255, 255)),
        ("white", 128, (147, 167, 187)),
        ("white", 255, (40, 80, 120)),
        ("black", 0, (0, 0, 0)),
        ("black", 128, (20, 40, 60)),
        ("black", 255, (40, 80, 120)),
        ("#204060", 0, (32, 64, 96)),
        ("#204060", 128, (36, 72, 108)),
        ("#204060", 255, (40, 80, 120)),
    ],
)
def test_rgba_background(
    tmp_path,
    size_option,
    expected_size,
    format_option,
    expected_format,
    background_color,
    alpha,
    expected_color,
):
    src = tmp_path / "input.png"
    dst = tmp_path / "output.png"
    Image.new("RGBA", (32, 32), (40, 80, 120, alpha)).save(src, dpi=(144, 144))
    _, options = parse_image_options(
        f"{format_option}background@{background_color}{size_option}", 95
    )

    _, status = process_image(src, dst, None, options)

    assert f"background@{background_color}" in status
    with Image.open(dst) as result:
        assert result.format == expected_format
        assert result.mode == "RGB"
        assert result.size == (expected_size, expected_size)
        assert result.getpixel((0, 0)) == pytest.approx(
            expected_color, abs=2 if expected_format == "JPEG" else 0
        )
        if size_option or expected_format == "PNG":
            assert result.info["dpi"] == pytest.approx(
                (72, 72) if size_option else (144, 144), abs=0.03
            )


@pytest.mark.parametrize("size_option,expected_size", [("", 32), (",16px", 16)])
@pytest.mark.parametrize("alpha", [0, 128, 255])
def test_rgba_to_jpeg_without_background(tmp_path, size_option, expected_size, alpha):
    src = tmp_path / "input.png"
    dst = tmp_path / "output.png"
    Image.new("RGBA", (32, 32), (40, 80, 120, alpha)).save(src)
    _, options = parse_image_options(f"jpeg{size_option}", 95)

    process_image(src, dst, None, options)

    with Image.open(dst) as result:
        assert result.size == (expected_size, expected_size)
        if alpha == 255:
            assert result.format == "JPEG"
            assert result.mode == "RGB"
        else:
            assert result.format == "PNG"
            assert result.mode == "RGBA"
            assert result.getchannel("A").getextrema() == (alpha, alpha)
            if not size_option:
                assert dst.read_bytes() == src.read_bytes()


@pytest.mark.parametrize("size_option,expected_size", [("", 32), (",16px", 16)])
def test_png_without_background_preserves_transparency(
    tmp_path, size_option, expected_size
):
    src = tmp_path / "input.png"
    dst = tmp_path / "output.png"
    Image.new("RGBA", (32, 32), (40, 80, 120, 128)).save(src)
    _, options = parse_image_options(size_option.lstrip(","), 95)

    process_image(src, dst, None, options)

    with Image.open(dst) as result:
        assert result.format == "PNG"
        assert result.mode == "RGBA"
        assert result.size == (expected_size, expected_size)
        assert result.getchannel("A").getextrema() == (128, 128)


@pytest.mark.parametrize("size_option,expected_size", [("", 32), (",16px", 16)])
@pytest.mark.parametrize("format_option,expected_format", [("", "PNG"), ("jpeg,", "JPEG")])
@pytest.mark.parametrize("mode", ["LA", "P", "L", "RGB"])
def test_white_background_other_png_transparency(
    tmp_path, size_option, expected_size, format_option, expected_format, mode
):
    src = tmp_path / "input.png"
    dst = tmp_path / "output.png"
    im = Image.new(mode, (32, 32))
    if mode in ("P", "L"):
        im.info["transparency"] = 0
    elif mode == "RGB":
        im.info["transparency"] = (0, 0, 0)
    im.save(src)
    _, options = parse_image_options(f"{format_option}background@white{size_option}", 95)

    process_image(src, dst, None, options)

    with Image.open(dst) as result:
        assert result.format == expected_format
        assert result.mode == "RGB"
        assert result.size == (expected_size, expected_size)
        assert result.getpixel((0, 0)) == (255, 255, 255)
        assert "transparency" not in result.info


@pytest.mark.parametrize("image_format", ["PNG", "JPEG"])
def test_background_without_transparency_copies_image(tmp_path, image_format):
    src = tmp_path / "input"
    dst = tmp_path / "output"
    Image.new("RGB", (32, 32), (40, 80, 120)).save(src, image_format)
    _, options = parse_image_options("background@white", 95)

    _, status = process_image(src, dst, None, options)

    assert status is None
    assert dst.read_bytes() == src.read_bytes()
