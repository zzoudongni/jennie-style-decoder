#!/usr/bin/env python3
"""Normalize a questionnaire response into neutral styling priorities."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


TOP_FIT = {
    "shoulder_ok_chest_tight": "保留清晰肩线，为胸部增加省道、弹性或前开口余量；不要只靠放大肩部解决。",
    "chest_ok_shoulder_waist_loose": "优先有意的短方形轮廓、可调腰或局部修改，区分设计感宽松与意外空量。",
    "shoulder_tight": "先保证肩部和上背活动量；落肩只在整体本就宽松时使用。",
    "sleeves_long": "可保留衣身的宽松感，但缩短、卷起或翻折袖长。",
    "sleeves_short": "选择明确的七分袖，或单独寻找足够袖长，不让它停在尴尬位置。",
    "tops_bulky": "减少厚面料和层数，以轮廓、配色或五金保留对比。",
    "none": "上装暂不设固定修正，试穿时观察肩线、活动量与内外层关系。",
    "unsure": "上装信息不足；先用一件合身内层和一件可开合外套做对照试穿。",
}
PANTS_FIT = {
    "waist_ok_hip_thigh_tight": "为臀腿增加余量，再单独处理腰部；优先直筒或宽松直线，不用紧绷换取所谓利落。",
    "hips_ok_waist_loose": "以臀部坐围舒适为先，用改腰、内调节或腰带处理腰部，不建议直接缩小整码。",
    "rise_issue": "做坐下和抬腿测试后，先比较不同前后裆、腰头弧度和尺码的真实低腰版型；只有用户主动想换时，才用视觉腰带或上衣长度作为替代。",
    "pants_long": "调整裤脚或选择合适内长；堆叠只能是有意且不影响行走的效果。",
    "pants_short": "选择明确九分线或更长内长，避免介于九分与全长之间的偶然长度。",
    "none": "裤装暂不设固定修正，重点测试腰头、坐围和裤脚断点。",
    "unsure": "裤装信息不足；用同一双鞋比较直筒与宽松裤的腰头、坐围和裤脚。",
}
GOALS = {
    "longer_lower_line": "用同色裤鞋、受控裤脚断点和清晰上下装交界，建立更连贯的下半身线条。",
    "lighter_upper": "一次只保留一层上身量感，选较轻面料、清洁领口或敞开前襟。",
    "defined_waist": "让衣摆、扣合点、腰带或短外套靠近自然腰，明确视觉交界。",
    "ease_hips_thighs": "把腰部固定与臀腿余量分开解决，面料应顺滑掠过而非贴紧。",
    "shoulder_presence": "用明确肩缝或短方形外套增加肩部存在感，下装保持更安静。",
    "more_curves": "用收放关系、接缝和材质对比制造曲线，不需要全身紧身。",
    "cleaner_lines": "减少竞争性的衣摆、颜色和配饰，重复一个主色并保留一个焦点。",
    "learn_logic": "不以修饰身材为目标，优先练习体积对比、颜色层级和单一焦点。",
}
SCENARIOS = {"commute", "school", "casual", "city_travel", "date", "island_holiday", "nightlife", "festival", "formal", "other"}
EXPOSURE = {"low", "medium", "high"}
INTENSITY = {"quiet", "flexible", "bold"}
TEMPERATURE_CONTEXTS = {
    "hot_humid": "炎热",
    "mild": "温和",
    "cold": "寒冷",
    "unsure": "不确定",
}
WEAR_ENVIRONMENTS = {
    "indoor": "全程室内",
    "indoor_brief_outdoor": "室内为主，短暂室外",
    "mixed": "室内外各半",
    "outdoor": "室外为主",
    "unsure": "不确定",
}
LEGACY_WEATHER_CONTEXTS = {
    "hot_humid", "mild", "cold_brief_outdoor", "cold_long_outdoor", "mainly_indoor", "unsure"
}
PREFERRED_ELEMENTS = {
    "low_neckline": "低胸或深领口",
    "low_rise": "真实低腰裤或低腰裙",
    "strapless": "抹胸",
    "camisole": "吊带或细肩带",
    "midriff": "露腰或短上衣",
    "underwear_as_outerwear": "underwear-as-outerwear",
    "lace": "蕾丝",
    "sheer": "透视纱或薄纱叠层",
    "micro_bottom": "超短下装",
    "high_slit": "高开衩",
    "backless": "露背",
    "tall_boots": "长靴",
    "stacked_hardware": "多层腰带、腰封或五金",
}
ELEMENT_STATES = {"often_wear", "willing_to_try", "not_now"}
MATERIALS = {
    "cotton": "纯棉或T恤面料",
    "knit": "针织",
    "denim": "牛仔",
    "technical": "速干、尼龙或运动机能面料",
    "linen": "亚麻",
    "satin_silklike": "缎面或丝感面料",
    "lace": "蕾丝",
    "sheer_mesh": "透视纱或网纱",
    "leather": "皮革或皮革感材质",
    "suede": "麂皮或麂皮感材质",
    "feather_fringe_fuzzy": "羽毛、流苏或毛绒质感",
}
STYLE_TAGS = {
    "minimal_basics": "极简基础",
    "casual_chill": "休闲慵懒或chill",
    "sport_technical": "运动机能",
    "feminine_romantic": "女性化或浪漫",
    "bold_sexy": "性感大胆",
    "cool_street": "酷感或街头",
    "classic_polished": "经典精致",
    "experimental_mix": "实验性混搭",
    "unsure": "不确定",
}

SCHEMA = {
    "height_cm": "number, 120–220",
    "top_fit": sorted(TOP_FIT),
    "pants_fit": sorted(PANTS_FIT),
    "garment_waist_position": ["above_natural_waist", "at_natural_waist", "below_natural_waist", "unsure", "rarely_wear"],
    "goals": sorted(GOALS),
    "scenario": "one value or an array from: " + ", ".join(sorted(SCENARIOS)),
    "temperature_context": sorted(TEMPERATURE_CONTEXTS),
    "wear_environment": sorted(WEAR_ENVIRONMENTS),
    "weather_context": "legacy optional value; use temperature_context and wear_environment for new responses",
    "exposure": sorted(EXPOSURE),
    "intensity": sorted(INTENSITY),
    "element_preferences": {"<element>": sorted(ELEMENT_STATES), "allowed_elements": sorted(PREFERRED_ELEMENTS)},
    "preferred_elements": "legacy optional array; use element_preferences for new responses",
    "current_materials": sorted(MATERIALS),
    "open_to_materials": sorted(MATERIALS),
    "current_style": sorted(STYLE_TAGS),
    "target_style": sorted(STYLE_TAGS),
    "measurements_cm": {"bust": "optional number", "waist": "optional number", "hip": "optional number", "waist_to_floor": "optional number"},
    "notes": "optional string",
}


def fail(message: str) -> None:
    raise ValueError(message)


def require_list(data: dict, key: str, allowed: dict[str, str], max_items: int | None = None) -> list[str]:
    value = data.get(key, [])
    if not isinstance(value, list):
        fail(f"{key} must be an array")
    unknown = [item for item in value if item not in allowed]
    if unknown:
        fail(f"{key} contains unsupported values: {unknown}")
    if max_items is not None and len(value) > max_items:
        fail(f"{key} accepts at most {max_items} values")
    return value


def normalize(data: dict) -> dict:
    height = data.get("height_cm")
    if not isinstance(height, (int, float)) or isinstance(height, bool) or not 120 <= height <= 220:
        fail("height_cm must be a number between 120 and 220")

    top_fit = require_list(data, "top_fit", TOP_FIT)
    pants_fit = require_list(data, "pants_fit", PANTS_FIT)
    goals = require_list(data, "goals", GOALS, max_items=2)

    raw_scenario = data.get("scenario")
    scenarios = raw_scenario if isinstance(raw_scenario, list) else [raw_scenario]
    if not scenarios or any(item not in SCENARIOS for item in scenarios):
        fail(f"scenario must be one value or an array from {sorted(SCENARIOS)}")
    exposure = data.get("exposure")
    if exposure not in EXPOSURE:
        fail(f"exposure must be one of {sorted(EXPOSURE)}")
    intensity = data.get("intensity", "flexible")
    if intensity not in INTENSITY:
        fail(f"intensity must be one of {sorted(INTENSITY)}")
    temperature_context = data.get("temperature_context")
    wear_environment = data.get("wear_environment")
    legacy_weather = data.get("weather_context")
    if temperature_context is None and wear_environment is None and legacy_weather is not None:
        if legacy_weather not in LEGACY_WEATHER_CONTEXTS:
            fail(f"weather_context must be one of {sorted(LEGACY_WEATHER_CONTEXTS)}")
        legacy_mapping = {
            "hot_humid": ("hot_humid", "unsure"),
            "mild": ("mild", "unsure"),
            "cold_brief_outdoor": ("cold", "indoor_brief_outdoor"),
            "cold_long_outdoor": ("cold", "outdoor"),
            "mainly_indoor": ("unsure", "indoor"),
            "unsure": ("unsure", "unsure"),
        }
        temperature_context, wear_environment = legacy_mapping[legacy_weather]
    temperature_context = temperature_context or "unsure"
    wear_environment = wear_environment or "unsure"
    if temperature_context not in TEMPERATURE_CONTEXTS:
        fail(f"temperature_context must be one of {sorted(TEMPERATURE_CONTEXTS)}")
    if wear_environment not in WEAR_ENVIRONMENTS:
        fail(f"wear_environment must be one of {sorted(WEAR_ENVIRONMENTS)}")
    preferred_elements = require_list(data, "preferred_elements", PREFERRED_ELEMENTS)
    raw_element_preferences = data.get("element_preferences", {}) or {}
    if not isinstance(raw_element_preferences, dict):
        fail("element_preferences must be an object")
    unknown_elements = [key for key in raw_element_preferences if key not in PREFERRED_ELEMENTS]
    invalid_states = [value for value in raw_element_preferences.values() if value not in ELEMENT_STATES]
    if unknown_elements:
        fail(f"element_preferences contains unsupported elements: {unknown_elements}")
    if invalid_states:
        fail(f"element_preferences contains unsupported states: {invalid_states}")
    active_elements = list(dict.fromkeys(preferred_elements + [
        key for key, value in raw_element_preferences.items() if value in {"often_wear", "willing_to_try"}
    ]))
    current_materials = require_list(data, "current_materials", MATERIALS)
    open_to_materials = require_list(data, "open_to_materials", MATERIALS)
    current_style = require_list(data, "current_style", STYLE_TAGS, max_items=3)
    target_style = require_list(data, "target_style", STYLE_TAGS, max_items=3)

    waist_position = data.get("garment_waist_position", "unsure")
    allowed_waist = set(SCHEMA["garment_waist_position"])
    if waist_position not in allowed_waist:
        fail(f"garment_waist_position must be one of {sorted(allowed_waist)}")

    measurements = data.get("measurements_cm", {}) or {}
    if not isinstance(measurements, dict):
        fail("measurements_cm must be an object")
    accepted_measurements: dict[str, float] = {}
    for key in ("bust", "waist", "hip", "waist_to_floor"):
        value = measurements.get(key)
        if value is None:
            continue
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not 30 <= value <= 180:
            fail(f"measurements_cm.{key} must be between 30 and 180 cm when supplied")
        accepted_measurements[key] = value

    exposure_note = {
        "low": "不要求露肤；用领口、贴合度、腰带或透视叠穿在不露肤的前提下建立焦点。",
        "medium": "通常突出一个露肤区域，也可以按个人意图组合锁骨、腰部、背部或腿部。",
        "high": "短款、真实低腰、underwear-as-outerwear、露背、透视或迷你元素可以作为第一选择；活动测试只用于优化固定与舒适。",
    }[exposure]
    intensity_note = {
        "quiet": "先给克制造型；大胆版本只作为可选对照。",
        "flexible": "根据每个具体场景同时比较安静版与大胆版，不预设哪一种更适合普通人。",
        "bold": "先给与参考图同等强度的方案，不自动降低露肤、低腰、材质或配饰戏剧性。",
    }[intensity]
    if temperature_context == "cold" and wear_environment == "indoor":
        climate_note = "室内目的地造型可保持原强度；路上增加长外套、保暖鞋履和外套寄存计划。"
    elif temperature_context == "cold" and wear_environment == "indoor_brief_outdoor":
        climate_note = "把途中与目的地拆开：室内造型保持原强度，短暂室外用长外套、保暖鞋履和方便脱穿的外层。"
    elif temperature_context == "cold" and wear_environment == "mixed":
        climate_note = "用同一公式建立外套穿上与脱下都完整的两种状态；保留核心交界与软硬冲突，同时加入薄保暖层。"
    elif temperature_context == "cold" and wear_environment == "outdoor":
        climate_note = "长时间室外时优先保暖：保留真实低腰、交界和软硬冲突，用长外套、薄保暖层、连裤袜或有内里的长靴减少持续暴露。"
    elif temperature_context == "hot_humid":
        climate_note = "高露肤可以直接保留；优先透气、轻薄或快干材质，并检查日晒、出汗、风和固定方式。"
    elif temperature_context == "mild":
        climate_note = "目的地造型保持原强度；有风或晚间降温时只增加一件容易移除的轻外层。"
    else:
        climate_note = "环境信息不足；用同一底层公式给室内外或冷暖切换，必要时只追问缺失的一项。"

    waist_notes = {
        "above_natural_waist": "成衣腰线常偏高：不要无条件再叠加高位宽腰带，先确认想要的视觉交界。",
        "at_natural_waist": "成衣腰线通常接近自然腰：短外套、收腰接缝和腰带较容易形成清晰交界。",
        "below_natural_waist": "成衣腰线常偏低：若想抬高视觉交界，可用敞开外套、短针织或同色腰带，而非强求高腰版型。",
        "unsure": "腰线位置暂不确定：先用自然腰处的一条细带做镜前对照，不据此下身材结论。",
        "rarely_wear": "缺少连衣裙/连体裤腰线经验：个性化方案不依赖这一项。",
    }

    return {
        "profile_summary": {
            "height_cm": height,
            "scenario": scenarios,
            "temperature_context": temperature_context,
            "temperature_context_label": TEMPERATURE_CONTEXTS[temperature_context],
            "wear_environment": wear_environment,
            "wear_environment_label": WEAR_ENVIRONMENTS[wear_environment],
            "exposure": exposure,
            "intensity": intensity,
            "element_preferences": raw_element_preferences,
            "preferred_elements": active_elements,
            "current_materials": current_materials,
            "open_to_materials": open_to_materials,
            "current_style": current_style,
            "target_style": target_style,
            "measurements_used": accepted_measurements,
        },
        "fit_responses": [TOP_FIT[item] for item in top_fit] + [PANTS_FIT[item] for item in pants_fit],
        "goal_priorities": [GOALS[item] for item in goals],
        "waist_guidance": waist_notes[waist_position],
        "exposure_guidance": exposure_note,
        "intensity_guidance": intensity_note,
        "climate_guidance": climate_note,
        "wardrobe_materials": {
            "current": [MATERIALS[item] for item in current_materials],
            "open_to_try": [MATERIALS[item] for item in open_to_materials],
        },
        "style_direction": {
            "current": [STYLE_TAGS[item] for item in current_style],
            "target": [STYLE_TAGS[item] for item in target_style],
        },
        "jennie_devices_to_test": [
            "合身或简洁内层 + 一件轮廓更明确的外层",
            "中性色底 + 一个叙事色",
            "女性化元素与实用/街头元素各一个",
            "只让一个配饰承担主要焦点",
        ] + [PREFERRED_ELEMENTS[item] for item in active_elements],
        "language_guardrail": "这是基于穿衣体验的造型假设，不是身材分类或价值判断。",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", nargs="?", type=Path, help="Questionnaire JSON file")
    parser.add_argument("--show-schema", action="store_true", help="Print the accepted JSON schema")
    args = parser.parse_args()

    if args.show_schema:
        print(json.dumps(SCHEMA, ensure_ascii=False, indent=2))
        return 0
    if args.profile is None:
        parser.error("profile is required unless --show-schema is used")

    try:
        data = json.loads(args.profile.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            fail("profile root must be an object")
        result = normalize(data)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
