"""SikshaSetu — ManimX animation of the student learning loop (diagnostic → mastery → bandit → test → report)."""
from manim import *


class LearningLoop(Scene):
    def construct(self):
        C = {"mastery": "#6D4AFF", "rec": "#2BD4AB", "test": "#F5C518", "report": "#FF5A5F"}
        title = Text("Adaptive Learning Loop", font_size=40).to_edge(UP)
        self.play(Write(title), run_time=0.8)

        def node(txt, color):
            return VGroup(Text(txt, font_size=18), Text(txt, font_size=11, color="#9aa0a6")).arrange(UP)

        boxes = {k: Rectangle(width=3.6, height=1.4, stroke_color=c) for k, c in C.items()}
        names = {"mastery": "Mastery\n(Elo)", "rec": "Bandit\n(Q-param)", "test": "Mock\nTest", "report": "Weak-point\nReport"}
        vs = {k: VGroup(Text(names[k], font_size=18), Text(names[k].split()[-1] + "\nupdates", font_size=11, color="#9aa0a6")).arrange(DOWN, buff=0.06).move_to(boxes[k]) for k in C}
        layout = {"mastery": LEFT * 0.55, "rec": LEFT * 0.55 + UP * 2.2, "test": DOWN * 1.6, "report": RIGHT * 0.55 + DOWN * 0.9}
        arrows = []
        for k in C:
            boxes[k].move_to(layout[k]); vs[k].move_to(boxes[k])
            self.play(FadeIn(boxes[k]), FadeIn(vs[k]), run_time=0.5)
        # diagnostic → mastery
        diag = Text("Diagnostic\n(adaptive Qs)", font_size=18, color=WHITE).next_to(UP + LEFT * 3, UP)
        a1 = Arrow(diag.get_center(), boxes["mastery"].get_center(), buff=0.6).set_color("#9aa0a6")
        self.play(Create(a1), run_time=0.5)
        # mastery → rec (prerequisite readiness)
        a2 = Arrow(boxes["mastery"].get_center(), boxes["rec"].get_center(), buff=0.6, max_stroke_width_to_length_ratio=30).set_color(C["mastery"])
        self.play(boxes["mastery"].animate.set_stroke(C["mastery"]), Create(a2), run_time=0.5)
        # rec → test
        a3 = Arrow(boxes["rec"].get_center(), boxes["test"].get_center(), buff=0.6).set_color(C["rec"])
        self.play(boxes["test"].animate.set_stroke(C["test"]), Create(a3), run_time=0.5)
        # test → report (and back to mastery)
        a4 = Arrow(boxes["test"].get_center(), boxes["report"].get_center(), buff=0.6).set_color(C["test"])
        a5 = Arrow(boxes["test"].get_center(), boxes["mastery"].get_center(), buff=0.6, max_stroke_width_to_length_ratio=20).set_color(C["rec"])
        self.play(boxes["report"].animate.set_stroke(C["report"]), Create(a4), Create(a5), run_time=0.5)
        # loop arrow: report → mastery (forget → decay re-study)
        # show 3 sigma animation: mastery bar fill
        bar = Rectangle(width=2.4, height=0.35, stroke_color="#6D4AFF", fill_color="#6D4AFF", fill_opacity=0.35).move_to(DOWN * 3)
        self.play(FadeIn(bar), FadeIn(Text("Mastery bar (0–10/unit)", font_size=16, color="#9aa0a6").next_to(bar, UP)), run_time=0.5)
        self.play(bar.animate.scale(2.2), run_time=0.9)
        self.wait(1.2)
