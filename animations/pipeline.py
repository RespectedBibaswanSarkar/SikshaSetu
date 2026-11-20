"""SikshaSetu — ManimX animation of the OCW→student pipeline."""
from manim import *


STAGES = ["resolve", "fetch", "parse", "transcode", "transcripts", "segment",
          "map", "questions", "package", "install", "verify"]


class PipelineAnim(Scene):
    def construct(self):
        V = VGroup()
        t = Text("SikshaSetu Pipeline", font_size=44).to_edge(UP)
        self.play(Write(t), run_time=0.8)
        box = Rectangle(width=4.4, height=1.0, stroke_color="#6D4AFF")
        self.play(Create(box), run_time=0.6)
        label = Text(STAGES[0], font_size=22, color=WHITE).move_to(box)
        self.play(FadeIn(label, scale=1.2), run_time=0.5)
        for s in STAGES[1:]:
            nl = Text(s, font_size=22, color=WHITE)
            nl.move_to(box)
            self.play(FadeOut(label, scale=0.5), FadeIn(nl, scale=1.2),
                      box.animate.set_stroke(GREEN), run_time=0.45)
            label = nl
        self.play(box.animate.set_stroke(PINK), run_time=0.3)
        done = Text("✓ store/catalog/concepts/questions ready", font_size=24, color=GREEN).next_to(box, DOWN)
        self.play(Write(done, run_time=0.8))
        self.wait(1.2)
