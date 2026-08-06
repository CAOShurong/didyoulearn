# Research landscape and project decision

Last reviewed: 2026-08-06

## Decision

DidYouLearn is a **go**, but not as another rubric-based tutor-response benchmark.

The defensible gap is a provider-neutral, open-source study system that compares frontier AI
products using outcomes from real learners: unaided post-test performance, transfer to new
problems, delayed retention, and the gap between perceived and demonstrated understanding.
Correctness is a gate, not a compensable style score.

## What already exists

| Work | What it measures | Boundary that remains |
|---|---|---|
| ELI-Why | Whether explanations fit learner information needs and educational levels | Mainly single explanations; does not rank tutors by measured learner gain |
| MRBench | Human-annotated pedagogical qualities in mathematical tutoring responses | Response-level rubric; mathematics-focused |
| MathTutorBench | Open-ended mathematical tutoring skills and a pedagogical reward model | Primarily automated response evaluation; not a public human-outcome arena |
| TutorBench | Adaptivity, correctness, and pedagogy in multi-turn sessions | Expert rubric and automated judge are proxies for actual learning |
| TeachBench | Post-instruction performance after syllabus-grounded teaching | Uses an LLM proxy learner and Gaokao-centered material |
| LearnLM evaluations | Expert preference, pedagogy principles, and product-specific trials | Primarily evaluates Google's tutor; no open cross-product public protocol |
| Harvard PS2 Pal RCT | Learning gain from a carefully structured AI physics tutor | One engineered tutor and course context, not a reusable model arena |

## Why outcome measurement matters

Solving ability and teaching ability are related but not interchangeable. A fluent explanation can
also increase a learner's confidence without supporting unaided performance. DidYouLearn therefore
separates:

1. correctness;
2. immediate mastery;
3. transfer;
4. retention;
5. confidence calibration;
6. time-normalized learning efficiency.

## Sources

- Joshi et al. (2025), [ELI-Why](https://aclanthology.org/2025.findings-acl.1306/).
- Maurya et al. (2025), [Unifying AI Tutor Evaluation](https://aclanthology.org/2025.naacl-long.57/).
- Macina et al. (2025), [MathTutorBench](https://aclanthology.org/2025.emnlp-main.11/).
- Li et al. (2026), [TeachBench](https://arxiv.org/abs/2601.21375).
- Google, [LearnLM](https://cloud.google.com/solutions/learnlm).
- Kestin et al. (2025), [AI tutoring RCT](https://www.nature.com/articles/s41598-025-97652-6).
- Bastani et al. (2025), [Generative AI without guardrails can harm learning](https://doi.org/10.1073/pnas.2422633122).
- Wan (2020), [Analysis of randomized pre-post designs](https://arxiv.org/abs/2007.07881).

## Claims this project will not make

- A synthetic demonstration proves that one commercial model teaches better.
- One learner's preferred explanation generalizes to other learners.
- A self-submitted transcript proves model identity.
- Immediate post-test improvement proves durable learning.
- A large number of generated tasks compensates for weak task review.
- A leaderboard is valid without uncertainty, sample thresholds, and protocol disclosure.
