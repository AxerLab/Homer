"""Mechanical post-processing to fix common Pydantic validation failures in LLM-generated presentation dicts.

Pure function: dict in, dict out. No dependencies on agents, models, config, or LLM providers.
Temporary workaround — remove when upstream model compliance improves.
"""

from copy import deepcopy

_TITLE_LAYOUTS = {"title_only", "title_and_content"}
_VALID_LAYOUTS = {
    "title", "title_and_content", "section_header", "two_content",
    "comparison", "title_only", "blank", "content_with_caption", "picture_with_caption",
}

_LAYOUT_LIMITS: dict[str, dict[str, int | None]] = {
    "title_and_content": {"max_bullets": 5, "max_bullet_len": 80, "max_para_len": 200},
    "picture_with_caption": {"max_bullets": 0, "max_bullet_len": None, "max_para_len": 120},
    "two_content": {"max_bullets": 4, "max_bullet_len": 60, "max_para_len": 150},
    "comparison": {"max_bullets": 4, "max_bullet_len": 50, "max_para_len": None},
    "content_with_caption": {"max_bullets": 4, "max_bullet_len": 60, "max_para_len": 150},
}

_DEFAULT_LIMITS = {"max_bullets": 5, "max_bullet_len": 80, "max_para_len": 200}


def fix_presentation_dict(data: dict) -> dict:
    """Fix common validation failures. Returns a corrected copy, never mutates input."""
    data = deepcopy(data)
    slides = data.get("slides")
    if not isinstance(slides, list) or not slides:
        return data

    slides = [_ensure_valid_layout(s) for s in slides[:20]]

    _fix_first_slide(slides)
    _fix_consecutive_title_only(slides)
    _ensure_image_slide(slides)

    for slide in slides:
        _fix_layout_content_rules(slide)
        _fix_content_limits(slide)

    data["slides"] = slides
    return data


def _ensure_valid_layout(slide: dict) -> dict:
    layout = slide.get("layout", "")
    if layout not in _VALID_LAYOUTS:
        slide["layout"] = "title_and_content"
    return slide


def _fix_first_slide(slides: list[dict]) -> None:
    if not slides:
        return
    if slides[0].get("layout") not in _TITLE_LAYOUTS:
        slides[0]["layout"] = "title_and_content"
        _ensure_text_content(slides[0])


def _fix_consecutive_title_only(slides: list[dict]) -> None:
    for i in range(1, len(slides)):
        if slides[i - 1].get("layout") == "title_only" and slides[i].get("layout") == "title_only":
            slides[i]["layout"] = "section_header"
            title = slides[i].get("title", "")
            content = slides[i].get("content") or {}
            text = content.get("text") or {}
            if not text.get("para"):
                text["para"] = title[:120] if title else "Section overview"
                text["bullet"] = []
                content["text"] = text
                slides[i]["content"] = content


def _ensure_image_slide(slides: list[dict]) -> None:
    for slide in slides:
        if slide.get("image"):
            layout = slide.get("layout", "")
            if layout == "picture_with_caption":
                return
            if layout == "two_content" and slide.get("image_position"):
                return

    best_idx = len(slides) // 2
    for i, slide in enumerate(slides):
        if i == 0:
            continue
        if slide.get("layout") in ("title_and_content", "content_with_caption", "section_header"):
            best_idx = i
            break

    if best_idx == 0 and len(slides) > 1:
        best_idx = 1

    target = slides[best_idx]
    title = target.get("title", "Illustration")
    target["layout"] = "picture_with_caption"
    target["image"] = title if title else "relevant illustration"
    target["image_position"] = None

    content = target.get("content") or {}
    text = content.get("text") or {}
    para = text.get("para", "")
    if not para:
        bullets = text.get("bullet", [])
        para = bullets[0][:120] if bullets else title[:120] if title else "Visual representation"
    else:
        para = para[:120]
    content["text"] = {"para": para, "bullet": []}
    content["text2"] = None
    content["comparison"] = None
    target["content"] = content


def _fix_layout_content_rules(slide: dict) -> None:
    layout = slide.get("layout", "")
    content = slide.get("content")

    if layout == "title_only":
        if not slide.get("title", "").strip():
            slide["title"] = "Untitled"
        slide["content"] = {"text": None, "text2": None, "comparison": None}
        return

    if layout == "blank":
        slide["title"] = ""
        slide["content"] = {"text": None, "text2": None, "comparison": None}
        return

    if content is None:
        content = {}
        slide["content"] = content

    if layout == "comparison":
        content.pop("text", None)
        content.pop("text2", None)
        comp = content.get("comparison") or {}
        for field in ("left_title", "right_title"):
            if not comp.get(field):
                comp[field] = "Side A" if "left" in field else "Side B"
        for field in ("left_content", "right_content"):
            if not comp.get(field):
                comp[field] = ["Point 1"]
        content["comparison"] = comp
        return

    if layout != "comparison":
        content.pop("comparison", None)

    if layout == "title_and_content":
        _ensure_text_content(slide)

    if layout == "section_header":
        text = content.get("text") or {}
        if not text.get("para"):
            title = slide.get("title", "")
            text["para"] = title[:120] if title else "Section overview"
        text["bullet"] = []
        content["text"] = text

    if layout == "two_content":
        if slide.get("image"):
            pos = slide.get("image_position")
            if not pos:
                slide["image_position"] = "right"
                pos = "right"
            if pos == "left":
                _ensure_text_field(content, "text2")
            else:
                _ensure_text_field(content, "text")
        else:
            slide["image_position"] = None
            _ensure_text_field(content, "text")
            _ensure_text_field(content, "text2")

    if layout == "content_with_caption":
        _ensure_text_field(content, "text")
        _ensure_text_field(content, "text2")

    if layout == "picture_with_caption":
        if not slide.get("image"):
            title = slide.get("title", "")
            slide["image"] = title if title else "relevant illustration"
        if not slide.get("title"):
            slide["title"] = "Image"
        text = content.get("text") or {}
        if text.get("bullet"):
            text["bullet"] = []
        if not text.get("para"):
            text["para"] = slide.get("title", "Caption")[:120]
        content["text"] = text


def _fix_content_limits(slide: dict) -> None:
    layout = slide.get("layout", "")
    limits = _LAYOUT_LIMITS.get(layout, _DEFAULT_LIMITS)
    content = slide.get("content")
    if not content:
        return

    for field in ("text", "text2"):
        tc = content.get(field)
        if not isinstance(tc, dict):
            continue

        max_para = limits.get("max_para_len")
        if max_para and tc.get("para"):
            tc["para"] = _truncate(tc["para"], max_para)

        max_bullets = limits.get("max_bullets", 5)
        max_bullet_len = limits.get("max_bullet_len")
        bullets = tc.get("bullet")
        if isinstance(bullets, list):
            if max_bullets == 0:
                tc["bullet"] = []
            else:
                bullets = bullets[:max_bullets]
                if max_bullet_len:
                    bullets = [_truncate(b, max_bullet_len) for b in bullets]
                tc["bullet"] = bullets

    comp = content.get("comparison")
    if isinstance(comp, dict):
        for field in ("left_content", "right_content"):
            items = comp.get(field)
            if isinstance(items, list):
                items = items[:4]
                items = [_truncate(b, 50) for b in items]
                comp[field] = items
        for field in ("left_title", "right_title"):
            val = comp.get(field)
            if isinstance(val, str) and len(val) > 100:
                comp[field] = _truncate(val, 100)


def _truncate(text: str, max_len: int) -> str:
    if not isinstance(text, str) or len(text) <= max_len:
        return text
    truncated = text[:max_len]
    last_space = truncated.rfind(" ")
    if last_space > max_len * 0.6:
        truncated = truncated[:last_space]
    return truncated.rstrip(".,;:!? ")


def _ensure_text_content(slide: dict) -> None:
    content = slide.get("content") or {}
    slide["content"] = content
    _ensure_text_field(content, "text")


def _ensure_text_field(content: dict, field: str) -> None:
    tc = content.get(field) or {}
    if not tc.get("para") and not tc.get("bullet"):
        tc["para"] = "Content"
    content[field] = tc
