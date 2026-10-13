"""Create a lightweight animated terminal-style demo GIF for the README."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parents[1] / "assets" / "demo.gif"
WIDTH, HEIGHT = 980, 470
FONT = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 22)
SMALL = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 17)
STEPS = [
    ("$ regulated-rag 'How long are customer documents retained?'", "#d8ff35"),
    ("→ retrieve      POL-RET-01  Retention and deletion", "#f4f1e8"),
    ("→ draft         cited answer created", "#f4f1e8"),
    ("→ evaluate      groundedness=1.0  citation_coverage=1.0", "#f4f1e8"),
    ("✓ approved      answer is policy-grounded", "#d8ff35"),
]


def frame(step_count: int) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#121312")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((20, 20, WIDTH - 20, HEIGHT - 20), radius=16, outline="#55544e", width=2)
    draw.ellipse((52, 48, 66, 62), fill="#ef8557")
    draw.ellipse((76, 48, 90, 62), fill="#d8ff35")
    draw.text((112, 42), "regulated-rag-evaluator", font=SMALL, fill="#f4f1e8")
    draw.text((52, 104), "LANGGRAPH / EVAL-GATED POLICY Q&A", font=SMALL, fill="#a8a69e")
    for index, (line, color) in enumerate(STEPS[:step_count]):
        draw.text((52, 150 + index * 53), line, font=FONT, fill=color)
    return image


frames = [frame(count) for count in range(1, len(STEPS) + 1)]
frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=[850, 650, 650, 800, 1600], loop=0)
print(OUT)

