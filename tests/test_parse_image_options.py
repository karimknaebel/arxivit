from pathlib import Path

import pytest

from arxivit import DpiValue, ImageOptions, PxValue, parse_image_options


@pytest.mark.parametrize(
    "opt,jpegq,expected",
    [
        (
            ":",
            95,
            (
                Path("abc"),
                ImageOptions(sizes=[], jpeg=False, jpeg_quality=95),
            ),
        ),
        (
            "",
            95,
            (
                Path("abc"),
                ImageOptions(sizes=[], jpeg=False, jpeg_quality=95),
            ),
        ),
        (
            "250dpi",
            95,
            (
                Path("."),
                ImageOptions(sizes=[DpiValue(250)], jpeg=False, jpeg_quality=95),
            ),
        ),
        (
            "jpeg",
            95,
            (Path("."), ImageOptions(sizes=[], jpeg=True, jpeg_quality=95)),
        ),
        (
            "100px,jpeg",
            95,
            (
                Path("."),
                ImageOptions(sizes=[PxValue(100)], jpeg=True, jpeg_quality=95),
            ),
        ),
        (
            "300dpi,jpeg",
            95,
            (
                Path("."),
                ImageOptions(sizes=[DpiValue(300)], jpeg=True, jpeg_quality=95),
            ),
        ),
        (
            "300dpi,jpeg,100px",
            95,
            (
                Path("."),
                ImageOptions(
                    sizes=[DpiValue(300), PxValue(100)], jpeg=True, jpeg_quality=95
                ),
            ),
        ),
        (
            "figures/qualitative:300dpi,jpeg",
            95,
            (
                Path("figures/qualitative"),
                ImageOptions(sizes=[DpiValue(300)], jpeg=True, jpeg_quality=95),
            ),
        ),
        (
            "figures/qualitative:300dpi,jpeg@60",
            95,
            (
                Path("figures/qualitative"),
                ImageOptions(sizes=[DpiValue(300)], jpeg=True, jpeg_quality=60),
            ),
        ),
        (
            "jpeg,background@white",
            95,
            (
                Path("."),
                ImageOptions(sizes=[], jpeg=True, jpeg_quality=95, background="white"),
            ),
        ),
        (
            "figures/*:background@#204060,300dpi,jpeg@60",
            95,
            (
                Path("figures/transparent.png"),
                ImageOptions(
                    sizes=[DpiValue(300)],
                    jpeg=True,
                    jpeg_quality=60,
                    background="#204060",
                ),
            ),
        ),
        (
            "background@black",
            95,
            (
                Path("."),
                ImageOptions(sizes=[], jpeg=False, jpeg_quality=95, background="black"),
            ),
        ),
    ],
)
def test_my(opt, jpegq, expected):
    match, image_options = parse_image_options(opt, jpegq)
    assert match(expected[0])
    assert image_options == expected[1]
